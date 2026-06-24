from __future__ import annotations

import copy
import json
import os
import random
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode

import requests
from flask import Flask, Response, jsonify, make_response, render_template, request
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dl_term_chat_image_secret")

APP_DIR = Path(__file__).resolve().parent
WORKFLOW_PATH = APP_DIR / "workflows" / "workflow.json"

COMFY_URL = os.environ.get("COMFYUI_BASE_URL", "http://localhost:8188").rstrip("/")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:e2b")

COOKIE_NAME = "dl_term_image_session_id"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7
MAX_HISTORY_MESSAGES = 10

DEFAULT_NEGATIVE_PROMPT = (
    "worst quality, low quality, blurry, bad anatomy, distorted, "
    "text, watermark, logo"
)

SYSTEM_PROMPT = """
You are an image prompt helper for a Korean deep learning class assignment.
The user will talk in Korean and gradually refine the image they want.

Your task:
1. Read the conversation history and the new user message.
2. Update one final image prompt in natural English for Stable Diffusion.
3. Reply in Korean with a short explanation of what changed.
4. Ask one short Korean follow-up question that helps refine the image further.
5. Always include the final prompt between these exact tags:
<FINAL_PROMPT>
English prompt here
</FINAL_PROMPT>

Keep the prompt concrete but not too long. Include subject, background, style,
lighting, color, composition, and important details when they are known.
Do not add unrelated details.
""".strip()

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

sessions: dict[str, dict] = {}
llm_executor = ThreadPoolExecutor(max_workers=2)


class AppError(RuntimeError):
    def __init__(self, code: str, message: str, status: int = 500):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


def get_or_create_session(req) -> str:
    session_id = req.cookies.get(COOKIE_NAME)
    if session_id:
        sessions.setdefault(session_id, {"messages": [], "current_prompt": "", "images": []})
        return session_id

    session_id = str(uuid.uuid4())
    sessions[session_id] = {"messages": [], "current_prompt": "", "images": []}
    return session_id


def response_with_cookie(payload, session_id: str, status: int = 200):
    response = jsonify(payload)
    response.status_code = status
    response.set_cookie(COOKIE_NAME, session_id, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax")
    return response


def get_history_messages(session_id: str) -> list[HumanMessage | AIMessage]:
    stored = sessions.get(session_id, {}).get("messages", [])[-MAX_HISTORY_MESSAGES:]
    messages: list[HumanMessage | AIMessage] = []
    for item in stored:
        if item["role"] == "user":
            messages.append(HumanMessage(content=item["content"]))
        else:
            messages.append(AIMessage(content=item["content"]))
    return messages


def get_ollama_models(timeout: float = 2) -> list[str]:
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=timeout)
    response.raise_for_status()
    return [model.get("name") for model in response.json().get("models", []) if model.get("name")]


def select_ollama_model() -> str:
    try:
        models = get_ollama_models()
    except Exception:
        return OLLAMA_MODEL

    if OLLAMA_MODEL in models:
        return OLLAMA_MODEL
    for model in models:
        if model.lower().startswith("gemma4"):
            return model
    for model in models:
        if model.lower().startswith("gemma"):
            return model
    return models[0] if models else OLLAMA_MODEL


@lru_cache(maxsize=4)
def build_chain(model_name: str):
    llm = ChatOllama(
        model=model_name,
        temperature=0.4,
        num_predict=512,
        base_url=OLLAMA_BASE_URL,
        client_kwargs={"timeout": 180},
    )
    return PROMPT | llm | StrOutputParser()


def extract_final_prompt(text: str) -> str:
    start_tag = "<FINAL_PROMPT>"
    end_tag = "</FINAL_PROMPT>"
    if start_tag in text and end_tag in text:
        start = text.index(start_tag) + len(start_tag)
        end = text.index(end_tag)
        return text[start:end].strip().strip('"').strip("'")
    return ""


def clean_assistant_reply(text: str) -> str:
    start_tag = "<FINAL_PROMPT>"
    if start_tag in text:
        text = text[: text.index(start_tag)]
    return text.strip() or "요구사항을 반영해서 현재 이미지 설명을 업데이트했습니다."


def ensure_refinement_question(reply: str) -> str:
    if "?" in reply or "？" in reply:
        return reply
    return f"{reply}\n\n더 구체화하려면 색감, 카메라 구도, 배경 디테일 중 무엇을 바꿀까요?"


def invoke_chain_with_timeout(model_name: str, payload: dict, timeout_sec: int = 180) -> str:
    future = llm_executor.submit(build_chain(model_name).invoke, payload)
    try:
        return future.result(timeout=timeout_sec)
    except FutureTimeoutError as exc:
        raise AppError(
            "OLLAMA_TIMEOUT",
            f"Ollama model '{model_name}' did not respond within {timeout_sec} seconds.",
            504,
        ) from exc


def load_workflow() -> dict:
    if not WORKFLOW_PATH.exists():
        raise AppError("WORKFLOW_MISSING", f"workflow.json file is missing: {WORKFLOW_PATH}", 500)
    with WORKFLOW_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


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
        raise AppError("COMFYUI_MODEL_LIST_FAILED", f"ComfyUI model list failed: {exc}", 502) from exc

    if not checkpoints:
        raise AppError(
            "COMFYUI_CHECKPOINT_MISSING",
            "No ComfyUI checkpoint found. Put a model file in comfyui_data/models/checkpoints and restart ComfyUI.",
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
    graph["9"]["inputs"]["filename_prefix"] = "dl_term_output"
    return graph


def post_prompt_to_comfyui(graph: dict) -> str:
    try:
        response = requests.post(f"{COMFY_URL}/prompt", json={"prompt": graph}, timeout=30)
    except requests.RequestException as exc:
        raise AppError("COMFYUI_UNREACHABLE", f"Cannot connect to ComfyUI API: {exc}", 502) from exc

    if response.status_code >= 400:
        raise AppError("COMFYUI_PROMPT_REJECTED", response.text[:1200], 502)

    payload = response.json()
    prompt_id = payload.get("prompt_id")
    if not prompt_id:
        raise AppError("COMFYUI_NO_PROMPT_ID", f"ComfyUI response has no prompt_id: {payload}", 502)
    return prompt_id


def poll_history(prompt_id: str, timeout_sec: int = 180, interval: float = 1.5) -> dict:
    deadline = time.time() + timeout_sec
    last_payload: dict | None = None

    while time.time() < deadline:
        response = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=10)
        response.raise_for_status()
        payload = response.json()

        if payload:
            last_payload = payload
            history_block = payload.get(prompt_id) or next(iter(payload.values()))
            status = history_block.get("status", {})
            if status.get("status_str") == "error":
                raise AppError("COMFYUI_GENERATION_ERROR", json.dumps(status.get("messages", []), ensure_ascii=False), 502)
            if history_block.get("outputs"):
                return history_block

        time.sleep(interval)

    raise AppError("COMFYUI_TIMEOUT", f"Image generation timed out. Last response: {last_payload}", 504)


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
                return f"/api/comfyui/view?{query}"
    raise AppError("COMFYUI_IMAGE_MISSING", "ComfyUI completed, but no output image was found.", 502)


def comfyui_health() -> dict:
    try:
        response = requests.get(f"{COMFY_URL}/system_stats", timeout=5)
        response.raise_for_status()
        checkpoints = get_comfyui_checkpoints()
        return {"ok": bool(checkpoints), "checkpoints": checkpoints}
    except Exception as exc:
        return {"ok": False, "checkpoints": [], "detail": str(exc)}


def ollama_health() -> dict:
    try:
        models = get_ollama_models()
        active_model = select_ollama_model()
        return {"ok": bool(models), "models": models, "active_model": active_model}
    except Exception as exc:
        return {"ok": False, "models": [], "active_model": OLLAMA_MODEL, "detail": str(exc)}


@app.route("/")
def index():
    session_id = get_or_create_session(request)
    session = sessions[session_id]
    active_model = select_ollama_model()
    response = make_response(
        render_template(
            "index.html",
            messages=session["messages"],
            current_prompt=session["current_prompt"],
            images=session["images"],
            active_model=active_model,
            default_negative=DEFAULT_NEGATIVE_PROMPT,
        )
    )
    response.set_cookie(COOKIE_NAME, session_id, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax")
    return response


@app.route("/api/status")
def status():
    session_id = get_or_create_session(request)
    session = sessions[session_id]
    return response_with_cookie(
        {
            "session_id": session_id,
            "model": select_ollama_model(),
            "current_prompt": session["current_prompt"],
            "message_count": len(session["messages"]),
            "image_count": len(session["images"]),
            "comfyui": comfyui_health(),
            "ollama": ollama_health(),
        },
        session_id,
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    session_id = get_or_create_session(request)
    session = sessions[session_id]
    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()

    if not user_input:
        return response_with_cookie({"code": "EMPTY_MESSAGE", "message": "메시지를 입력해 주세요."}, session_id, 400)

    previous_prompt = session.get("current_prompt") or "No prompt yet."
    chain_input = f"현재 이미지 설명: {previous_prompt}\n\n사용자 추가 요구사항: {user_input}"
    history_messages = get_history_messages(session_id)
    session["messages"].append({"role": "user", "content": user_input})

    try:
        active_model = select_ollama_model()
        raw_answer = invoke_chain_with_timeout(active_model, {"history": history_messages, "input": chain_input})
        final_prompt = extract_final_prompt(raw_answer)
        reply = ensure_refinement_question(clean_assistant_reply(raw_answer))
        if not final_prompt:
            final_prompt = session.get("current_prompt") or user_input
            reply = f"{reply}\n\n최종 프롬프트 태그가 없어 입력 내용을 기준으로 저장했습니다."

        session["current_prompt"] = final_prompt
        session["messages"].append({"role": "assistant", "content": reply})
        return response_with_cookie(
            {
                "reply": reply,
                "current_prompt": final_prompt,
                "model": active_model,
                "messages": session["messages"],
            },
            session_id,
        )
    except Exception as exc:
        return response_with_cookie({"code": "OLLAMA_CHAT_FAILED", "message": str(exc)}, session_id, 502)


@app.route("/api/generate", methods=["POST"])
def generate():
    session_id = get_or_create_session(request)
    session = sessions[session_id]
    data = request.get_json(silent=True) or {}

    positive_prompt = (data.get("prompt") or session.get("current_prompt") or "").strip()
    negative_prompt = (data.get("negative_prompt") or DEFAULT_NEGATIVE_PROMPT).strip()
    width = int(data.get("width") or 512)
    height = int(data.get("height") or 512)
    steps = int(data.get("steps") or 20)
    cfg = float(data.get("cfg") or 7)

    if not positive_prompt:
        return response_with_cookie(
            {"code": "EMPTY_PROMPT", "message": "먼저 채팅으로 만들 이미지 설명을 정리해 주세요."},
            session_id,
            400,
        )

    try:
        workflow = update_workflow(load_workflow(), positive_prompt, negative_prompt, width, height, steps, cfg)
        prompt_id = post_prompt_to_comfyui(workflow)
        history_block = poll_history(prompt_id)
        image_url = extract_first_image_url(history_block)
        result = {
            "prompt_id": prompt_id,
            "image_url": image_url,
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "settings": {"width": width, "height": height, "steps": steps, "cfg": cfg},
        }
        session["images"].insert(0, result)
        session["images"] = session["images"][:8]
        return response_with_cookie(result, session_id)
    except AppError as exc:
        return response_with_cookie({"code": exc.code, "message": exc.message}, session_id, exc.status)
    except Exception as exc:
        return response_with_cookie({"code": "UNKNOWN_ERROR", "message": str(exc)}, session_id, 500)


@app.route("/api/comfyui/view")
def comfyui_view():
    params = {
        "filename": request.args.get("filename", ""),
        "subfolder": request.args.get("subfolder", ""),
        "type": request.args.get("type", "output"),
    }
    if not params["filename"]:
        return jsonify({"code": "IMAGE_FILENAME_MISSING", "message": "이미지 파일명이 없습니다."}), 400

    try:
        upstream = requests.get(f"{COMFY_URL}/view", params=params, timeout=30)
        upstream.raise_for_status()
    except requests.RequestException as exc:
        return jsonify({"code": "COMFYUI_IMAGE_LOAD_FAILED", "message": str(exc)}), 502

    content_type = upstream.headers.get("Content-Type", "image/png")
    return Response(upstream.content, content_type=content_type)


@app.route("/api/clear", methods=["POST"])
def clear():
    session_id = get_or_create_session(request)
    sessions[session_id] = {"messages": [], "current_prompt": "", "images": []}
    return response_with_cookie({"status": "ok"}, session_id)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5104))
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)


