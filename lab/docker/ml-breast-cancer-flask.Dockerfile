FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace/lab/machine-learning/assignments/04-breast-cancer-flask

COPY machine-learning/assignments/04-breast-cancer-flask/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
