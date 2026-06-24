"""
공통 ComfyUI API 클라이언트 모듈
강의 자료(Chapter 3) API 흐름 기반으로 작성
흐름: POST /prompt → WebSocket 진행 감지 → GET /history/{prompt_id} → 이미지 반환
"""
import os
import uuid
import json
import time
import requests
import websocket

# ComfyUI 서버 주소 (환경 변수 또는 기본값)
COMFYUI_BASE_URL = os.environ.get("COMFYUI_BASE_URL", "http://localhost:8188")
COMFYUI_WS_URL   = COMFYUI_BASE_URL.replace("http://", "ws://")


def submit_prompt(workflow: dict) -> str:
    """
    워크플로우를 ComfyUI 큐에 제출하고 prompt_id 반환
    강의 자료 POST /prompt 방식
    """
    client_id = str(uuid.uuid4())
    payload   = {"prompt": workflow, "client_id": client_id}

    resp = requests.post(f"{COMFYUI_BASE_URL}/prompt", json=payload, timeout=30)
    resp.raise_for_status()

    data      = resp.json()
    prompt_id = data.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI 큐 제출 실패: {data}")
    return prompt_id, client_id


def wait_for_result(prompt_id: str, client_id: str, timeout: int = 120) -> list[str]:
    """
    WebSocket으로 실행 완료를 감지한 뒤 생성된 이미지 파일명 목록 반환
    강의 자료 웹소켓 → GET /history/{prompt_id} 방식
    """
    ws_url = f"{COMFYUI_WS_URL}/ws?clientId={client_id}"
    ws     = websocket.WebSocket()

    try:
        ws.connect(ws_url, timeout=timeout)
        deadline = time.time() + timeout

        while time.time() < deadline:
            raw = ws.recv()
            if not raw:
                continue
            msg = json.loads(raw)

            # 실행 완료 이벤트 감지
            if msg.get("type") == "execution_success":
                if msg.get("data", {}).get("prompt_id") == prompt_id:
                    break
    finally:
        ws.close()

    # 히스토리에서 생성된 이미지 파일명 추출
    return get_output_images(prompt_id)


def get_output_images(prompt_id: str) -> list[str]:
    """
    GET /history/{prompt_id} 로 생성 이미지 파일명 목록 반환
    """
    resp = requests.get(f"{COMFYUI_BASE_URL}/history/{prompt_id}", timeout=30)
    resp.raise_for_status()

    history = resp.json()
    images  = []

    outputs = history.get(prompt_id, {}).get("outputs", {})
    for node_output in outputs.values():
        for img in node_output.get("images", []):
            images.append(img.get("filename", ""))

    return [f for f in images if f]


def get_image_url(filename: str, subfolder: str = "", img_type: str = "output") -> str:
    """이미지 파일명으로 브라우저에서 접근 가능한 URL 생성"""
    params = f"filename={filename}&subfolder={subfolder}&type={img_type}"
    return f"{COMFYUI_BASE_URL}/view?{params}"


def load_workflow(json_path: str) -> dict:
    """workflow JSON 파일 로드"""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
