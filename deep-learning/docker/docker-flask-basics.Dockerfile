FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace/deep-learning/class-code/docker-flask-basics/chapter02/flaskserver

COPY class-code/docker-flask-basics/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

EXPOSE 5000

CMD ["python", "hello.py"]
