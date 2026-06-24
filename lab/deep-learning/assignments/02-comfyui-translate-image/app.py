from __future__ import annotations

import copy
import json
import os
import random
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)

APP_DIR = Path(__file__).resolve().parent
WORKFLOW_PATH = APP_DIR / "workflows" / "workflow.json"

COMFY_URL = os.environ.get("COMFYUI_BASE_URL", "http://localhost:8188").rstrip("/")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:e2b")

DEFAULT_NEGATIVE_PROMPT = (
    "worst quality, low quality, blurry, distorted hands, extra fingers, "
    "bad anatomy, text, watermark, logo"
)

TRANSLATE_SYSTEM_PROMPT = (
    "You are a Stable Diffusion prompt engineer. Convert the user's Korean image request "
    "into one polished English prompt for text-to-image generation. Preserve the user's "
    "intent, add helpful visual details only when they fit, and output only the final "
    "English prompt. Do not include Korean, markdown, quotes, explanations, or bullet points."
)

class AppError(RuntimeError):
    def __init__(self, code: str, message: str, status: int = 500):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


def load_workflow() -> dict:
    if not WORKFLOW_PATH.exists():
        raise AppError("WORKFLOW_MISSING", f"workflow.json 파일을 찾을 수 없습니다: {WORKFLOW_PATH}", 500)

    with WORKFLOW_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_ollama_models() -> list[str]:
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
    response.raise_for_status()
    return [item.get("name") for item in response.json().get("models", []) if item.get("name")]


def select_ollama_model() -> str:
    try:
        models = get_ollama_models()
    except Exception:
        return OLLAMA_MODEL
    if OLLAMA_MODEL in models:
        return OLLAMA_MODEL
    for model in models:
        if model.lower().startswith("gemma"):
            return model
    if models:
        return models[0]
    return OLLAMA_MODEL


def get_comfyui_checkpoints() -> list[str]:
    response = requests.get(f"{COMFY_URL}/object_info/CheckpointLoaderSimple", timeout=10)
    response.raise_for_status()
    node_info = response.json().get("CheckpointLoaderSimple", {})
    ckpt_field = node_info.get("input", {}).get("required", {}).get("ckpt_name", [])
    if ckpt_field and isinstance(ckpt_field[0], list):
        return ckpt_field[0]
    return []


def select_checkpoint(graph: dict) -> str:
    try:
        checkpoints = get_comfyui_checkpoints()
    except Exception as exc:
        raise AppError("COMFYUI_MODEL_LIST_FAILED", f"ComfyUI 모델 목록을 읽지 못했습니다. 원인: {exc}", 502) from exc

    if not checkpoints:
        raise AppError(
            "COMFYUI_CHECKPOINT_MISSING",
            "ComfyUI 체크포인트가 없습니다. comfyui_data/models/checkpoints 폴더에 Stable Diffusion checkpoint 파일을 넣은 뒤 ComfyUI를 재시작하세요.",
            502,
        )

    configured = graph.get("4", {}).get("inputs", {}).get("ckpt_name")
    return configured if configured in checkpoints else checkpoints[0]


def update_workflow(graph: dict, positive: str, negative: str, width: int, height: int, steps: int, cfg: float) -> dict:
    graph = copy.deepcopy(graph)
    graph["4"]["inputs"]["ckpt_name"] = select_checkpoint(graph)
    graph["3"]["inputs"]["seed"] = random.randint(1, 2**48)
    graph["3"]["inputs"]["steps"] = steps
    graph["3"]["inputs"]["cfg"] = cfg
    graph["5"]["inputs"]["width"] = width
    graph["5"]["inputs"]["height"] = height
    graph["6"]["inputs"]["text"] = positive
    graph["7"]["inputs"]["text"] = negative
    return graph


def translate_korean_prompt(korean_text: str) -> str:
    active_model = select_ollama_model()
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": active_model,
                "stream": False,
                "think": False,
                "messages": [
                    {"role": "system", "content": TRANSLATE_SYSTEM_PROMPT},
                    {"role": "user", "content": korean_text},
                ],
                "options": {
                    "temperature": 0.2,
                    "num_predict": 140,
                    "top_p": 0.8,
                },
            },
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
        translated = (payload.get("message", {}).get("content") or payload.get("response") or "").strip()
    except Exception as exc:
        raise AppError(
            "OLLAMA_TRANSLATE_FAILED",
            f"Ollama 번역 호출에 실패했습니다. 모델({active_model})과 주소({OLLAMA_BASE_URL})를 확인하세요. 원인: {exc}",
            502,
        ) from exc

    translated = translated.strip().strip('"').strip("'")
    if not translated:
        raise AppError("EMPTY_TRANSLATION", "LLM 번역 결과가 비어 있습니다. 프롬프트를 더 구체적으로 입력하세요.", 502)
    return translated


def post_prompt_to_comfyui(graph: dict) -> str:
    try:
        response = requests.post(f"{COMFY_URL}/prompt", json={"prompt": graph}, timeout=30)
    except requests.RequestException as exc:
        raise AppError(
            "COMFYUI_UNREACHABLE",
            f"ComfyUI API에 연결할 수 없습니다. 주소({COMFY_URL})와 실행 상태를 확인하세요. 원인: {exc}",
            502,
        ) from exc

    if response.status_code >= 400:
        raise AppError("COMFYUI_PROMPT_REJECTED", response.text[:1200], 502)

    payload = response.json()
    prompt_id = payload.get("prompt_id")
    if not prompt_id:
        raise AppError("COMFYUI_NO_PROMPT_ID", f"ComfyUI 응답에 prompt_id가 없습니다: {payload}", 502)
    return prompt_id


def poll_history(prompt_id: str, timeout_sec: int = 180, interval: float = 1.5) -> dict:
    deadline = time.time() + timeout_sec
    last_payload: dict | None = None

    while time.time() < deadline:
        try:
            response = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=10)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise AppError("COMFYUI_HISTORY_FAILED", f"ComfyUI history 조회에 실패했습니다. 원인: {exc}", 502) from exc

        if payload:
            last_payload = payload
            history_block = payload.get(prompt_id) or next(iter(payload.values()))
            status = history_block.get("status", {})
            if status.get("status_str") == "error":
                messages = status.get("messages", [])
                raise AppError("COMFYUI_GENERATION_ERROR", json.dumps(messages, ensure_ascii=False)[:1600], 502)
            if history_block.get("outputs"):
                return history_block

        time.sleep(interval)

    raise AppError("COMFYUI_TIMEOUT", f"{timeout_sec}초 안에 이미지 생성 결과를 받지 못했습니다. 마지막 응답: {last_payload}", 504)


def extract_first_image_url(history_block: dict) -> str:
    for node_output in history_block.get("outputs", {}).values():
        for image in node_output.get("images", []):
            filename = image.get("filename")
            if filename:
                query = urlencode(
                    {
                        "filename": filename,
                        "subfolder": image.get("subfolder", ""),
                        "type": image.get("type", "output"),
                    }
                )
                return f"{COMFY_URL}/view?{query}"
    raise AppError("COMFYUI_IMAGE_MISSING", "ComfyUI 실행은 끝났지만 저장된 이미지 정보를 찾지 못했습니다.", 502)


def comfyui_health() -> dict:
    try:
        response = requests.get(f"{COMFY_URL}/system_stats", timeout=5)
        response.raise_for_status()
        checkpoints = get_comfyui_checkpoints()
        return {"ok": bool(checkpoints), "checkpoints": checkpoints, "detail": response.json()}
    except Exception as exc:
        return {"ok": False, "checkpoints": [], "detail": str(exc)}


def ollama_health() -> dict:
    try:
        models = get_ollama_models()
        active_model = select_ollama_model()
        return {"ok": bool(models), "models": models, "configured_model": OLLAMA_MODEL, "active_model": active_model}
    except Exception as exc:
        return {"ok": False, "models": [], "configured_model": OLLAMA_MODEL, "active_model": OLLAMA_MODEL, "detail": str(exc)}


@app.route("/")
def index():
    return render_template(
        "index.html",
        comfy_url=COMFY_URL,
        ollama_url=OLLAMA_BASE_URL,
        ollama_model=OLLAMA_MODEL,
        default_negative=DEFAULT_NEGATIVE_PROMPT,
    )


@app.route("/api/health")
def health():
    return jsonify(
        {
            "comfyui": comfyui_health(),
            "ollama": ollama_health(),
            "workflow_exists": WORKFLOW_PATH.exists(),
            "workflow_path": str(WORKFLOW_PATH),
            "comfy_url": COMFY_URL,
            "ollama_url": OLLAMA_BASE_URL,
            "ollama_model": OLLAMA_MODEL,
        }
    )


@app.route("/api/translate_only", methods=["POST"])
def translate_only():
    data = request.get_json(silent=True) or {}
    korean_input = (data.get("korean_input") or "").strip()
    if not korean_input:
        return jsonify({"code": "EMPTY_PROMPT", "error": "한글 프롬프트를 입력하세요."}), 400

    try:
        return jsonify({"eng_prompt": translate_korean_prompt(korean_input)})
    except AppError as exc:
        return jsonify({"code": exc.code, "error": exc.message}), exc.status


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    korean_input = (data.get("korean_input") or "").strip()
    negative_prompt = (data.get("neg_prompt") or DEFAULT_NEGATIVE_PROMPT).strip()
    width = int(data.get("width") or 512)
    height = int(data.get("height") or 512)
    steps = int(data.get("steps") or 20)
    cfg = float(data.get("cfg") or 7)

    if not korean_input:
        return jsonify({"code": "EMPTY_PROMPT", "error": "한글 프롬프트를 입력하세요."}), 400

    try:
        english_prompt = translate_korean_prompt(korean_input)
        workflow = update_workflow(load_workflow(), english_prompt, negative_prompt, width, height, steps, cfg)
        prompt_id = post_prompt_to_comfyui(workflow)
        history_block = poll_history(prompt_id)
        image_url = extract_first_image_url(history_block)
        return jsonify(
            {
                "korean_input": korean_input,
                "eng_prompt": english_prompt,
                "neg_prompt": negative_prompt,
                "img_url": image_url,
                "prompt_id": prompt_id,
                "settings": {"width": width, "height": height, "steps": steps, "cfg": cfg},
            }
        )
    except AppError as exc:
        return jsonify({"code": exc.code, "error": exc.message}), exc.status
    except Exception as exc:
        return jsonify({"code": "UNKNOWN_ERROR", "error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5102))
    app.run(host="0.0.0.0", port=port, debug=True)



