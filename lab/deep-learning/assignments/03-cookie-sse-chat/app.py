from __future__ import annotations

import json
import os
import uuid
from functools import lru_cache

import requests
from flask import Flask, Response, jsonify, make_response, render_template, request, stream_with_context
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dl3_secret_key")

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:e2b")
COOKIE_NAME = "dl3_session_id"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7
MAX_HISTORY_MESSAGES = 12

SYSTEM_PROMPT = (
    "You are StreamDesk, a helpful Korean AI assistant for a local learning lab. "
    "Always answer in natural Korean. "
    "Keep responses practical, friendly, and concise. "
    "If the user asks about the chat system, explain cookie-based session restore and SSE streaming accurately in Korean."
)

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

# In-memory store for the assignment. A production version would move this to Redis or a database.
chat_store: dict[str, list[dict[str, str]]] = {}


def get_or_create_session(req) -> str:
    session_id = req.cookies.get(COOKIE_NAME)
    if session_id:
        return session_id
    return str(uuid.uuid4())


def get_history_messages(session_id: str) -> list[HumanMessage | AIMessage]:
    stored = chat_store.get(session_id, [])[-MAX_HISTORY_MESSAGES:]
    messages: list[HumanMessage | AIMessage] = []
    for item in stored:
        if item["role"] == "user":
            messages.append(HumanMessage(content=item["content"]))
        else:
            messages.append(AIMessage(content=item["content"]))
    return messages


def get_ollama_models() -> list[str]:
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
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
        temperature=0.6, 
        base_url=OLLAMA_BASE_URL
        )
    return PROMPT | llm | StrOutputParser()


def sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.route("/")
def index():
    session_id = get_or_create_session(request)
    history = chat_store.get(session_id, [])
    active_model = select_ollama_model()

    response = make_response(render_template("index.html", history=history, active_model=active_model))
    response.set_cookie(COOKIE_NAME, session_id, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax")
    return response


@app.route("/api/status", methods=["GET"])
def status():
    session_id = get_or_create_session(request)
    active_model = select_ollama_model()
    response = jsonify(
        {
            "status": "ok",
            "session_id": session_id,
            "model": active_model,
            "base_url": OLLAMA_BASE_URL,
            "history_count": len(chat_store.get(session_id, [])),
            "cookie_name": COOKIE_NAME,
        }
    )
    response.set_cookie(COOKIE_NAME, session_id, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax")
    return response


@app.route("/api/history", methods=["GET"])
def history():
    session_id = get_or_create_session(request)
    response = jsonify({"session_id": session_id, "history": chat_store.get(session_id, [])})
    response.set_cookie(COOKIE_NAME, session_id, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax")
    return response


@app.route("/api/clear", methods=["POST"])
def clear_history():
    session_id = get_or_create_session(request)
    chat_store[session_id] = []
    response = jsonify({
        "status": "ok", 
        "message": "대화 기록을 삭제했습니다."
        })
    response.set_cookie(
        COOKIE_NAME, 
        session_id, 
        max_age=COOKIE_MAX_AGE, 
        httponly=True, 
        samesite="Lax")
    return response


@app.route("/api/stream", methods=["POST"])
def stream_chat():
    session_id = get_or_create_session(request)
    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()

    if not user_input:
        return jsonify({"code": "EMPTY_MESSAGE", "message": "메시지를 입력해 주세요."}), 400

    history_messages = get_history_messages(session_id)
    chat_store.setdefault(session_id, []).append({"role": "user", "content": user_input})

    @stream_with_context
    def generate():
        full_response = ""
        active_model = select_ollama_model()
        yield sse("open", {"status": "started", "model": active_model})

        try:
            chain = build_chain(active_model)
            for chunk in chain.stream({"history": history_messages, "input": user_input}):
                if not chunk:
                    continue
                full_response += chunk
                yield sse("token", {"text": chunk})
        except Exception as exc:
            yield sse("error", {"code": "OLLAMA_STREAM_FAILED", "message": str(exc)})
            return

        chat_store[session_id].append({"role": "ai", "content": full_response})
        yield sse("end", {"status": "done", "chars": len(full_response)})

    response = Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
    response.set_cookie(COOKIE_NAME, session_id, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax")
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5103))
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
