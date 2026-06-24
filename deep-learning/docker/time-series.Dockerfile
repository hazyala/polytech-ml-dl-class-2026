FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace/deep-learning/class-code/time-series

COPY class-code/time-series/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

EXPOSE 8890

CMD ["python", "-m", "jupyter", "lab", "--ip=0.0.0.0", "--port=8890", "--no-browser", "--allow-root", "--ServerApp.token=", "--ServerApp.password="]
