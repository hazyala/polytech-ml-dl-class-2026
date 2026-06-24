FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    COMFYUI_BASE_URL=http://host.docker.internal:8188 \
    OLLAMA_MODEL=gemma4:e2b \
    PORT=5102

WORKDIR /workspace/lab/deep-learning/assignments/02-comfyui-translate-image

COPY deep-learning/assignments/02-comfyui-translate-image/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

EXPOSE 5102

CMD ["python", "app.py"]
