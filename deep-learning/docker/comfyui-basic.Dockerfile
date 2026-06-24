FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    COMFYUI_BASE_URL=http://host.docker.internal:8188

WORKDIR /workspace/deep-learning/class-code/comfyui-basic

COPY class-code/comfyui-basic/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

CMD ["python", "queue_prompt_demo.py"]
