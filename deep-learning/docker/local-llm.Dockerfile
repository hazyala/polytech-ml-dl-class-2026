FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    OLLAMA_BASE_URL=http://host.docker.internal:11434

WORKDIR /workspace/deep-learning/class-code/local-llm

COPY class-code/local-llm/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

CMD ["python", "ollama_chat_demo.py"]
