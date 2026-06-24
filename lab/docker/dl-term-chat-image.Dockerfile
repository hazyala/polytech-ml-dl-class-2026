FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    COMFYUI_BASE_URL=http://host.docker.internal:8188 \
    OLLAMA_MODEL=gemma4:e2b \
    PORT=5104

WORKDIR /workspace/lab/deep-learning/term-projects/chat-image-generator

COPY deep-learning/term-projects/chat-image-generator/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

EXPOSE 5104

CMD ["python", "app.py"]
