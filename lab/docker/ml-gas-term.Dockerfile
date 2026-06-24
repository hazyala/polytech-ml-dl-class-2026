FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    GAS_LEAK_DATASET_DIR=/workspace/lab/datasets/gas-leak-sample

WORKDIR /workspace/lab/machine-learning/term-projects/gas-leak-prediction

COPY machine-learning/term-projects/gas-leak-prediction/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

EXPOSE 8889

CMD ["python", "-m", "jupyter", "lab", "--ip=0.0.0.0", "--port=8889", "--no-browser", "--allow-root", "--ServerApp.token=", "--ServerApp.password="]
