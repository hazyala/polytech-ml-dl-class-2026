FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    OLLAMA_MODEL=gemma4:e2b \
    PORT=5101

WORKDIR /workspace/lab/deep-learning/assignments/01-missionaries-cannibals-gm

COPY deep-learning/assignments/01-missionaries-cannibals-gm/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

EXPOSE 5101

CMD ["python", "app.py"]
