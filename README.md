# polytech-ml-dl-class-2026

ML/DL 수업 자료, 실습 코드, 과제 산출물을 한 저장소에서 보기 좋게 정리한 작업 공간입니다.

## 구조

- `lab/`: 과제와 텀프로젝트 산출물
- `machine-learning/class-code/`: 머신러닝 수업 시간 코드와 필기
- `machine-learning/examples/`: PDF 흐름을 따라 보강한 머신러닝 진입 예제
- `deep-learning/class-code/`: Docker, Flask API, Local LLM, LangChain, ComfyUI, 시계열 딥러닝 수업 코드
- `machine-learning/docker/`: 머신러닝 수업용 Docker 구성
- `deep-learning/docker/`: 딥러닝 수업용 Docker 구성
- `lab/docker/`: 과제와 텀프로젝트용 Docker 구성

## Lab 과제

과제로 보이는 기존 로컬 산출물은 `lab/` 아래로 모았습니다.

- `lab/deep-learning/assignments/`: DL 과제1, 과제2, 과제3
- `lab/deep-learning/term-projects/`: DL 텀프로젝트
- `lab/machine-learning/assignments/`: Iris/Kaggle/유방암 Flask/식인종-선교사 과제
- `lab/machine-learning/term-projects/`: ML 기초 텀프로젝트
- `lab/docs/PROJECT_DOCS.md`: 기존 통합 과제 환경 문서
- `lab/docs/COMFYUI_MODEL_DOWNLOAD.md`: ComfyUI checkpoint 다운로드 위치와 저장 경로
- `lab/docs/JENA_TIMESERIES_DATA_NOTE.md`: Jena 시계열 데이터셋 다운로드와 Keras 모델 재생성 안내

## 수업 코드

수업 중 작성된 코드와 노트북은 과제 폴더와 섞지 않고 별도로 모았습니다.

- `machine-learning/class-code/dated-classes/`: 날짜별 ML 수업 노트북/스크립트
- `machine-learning/class-code/chapters/`: PDF 챕터 흐름에 맞춘 ML 필기/예제
- `deep-learning/class-code/docker-flask-basics/`: Docker, WSL, Flask 기본 수업 자료
- `deep-learning/class-code/flask-api-basic/`: Python API 서버 진입 예제
- `deep-learning/class-code/local-llm/`: Ollama/Local LLM 예제
- `deep-learning/class-code/langchain-basic/`: LangChain 기본 체인 예제
- `deep-learning/class-code/langchain-memory-basic/`: LangChain memory 예제
- `deep-learning/class-code/comfyui-basic/`: ComfyUI API 예제
- `deep-learning/class-code/time-series/`: 시계열 딥러닝 노트북/예제

## 예제

PDF 흐름을 따라 바로 실행해볼 수 있는 작은 진입 예제를 추가했습니다.

- `machine-learning/examples/01_numpy_pandas_basics.py`
- `machine-learning/examples/02_probability_distance_metrics.py`
- `machine-learning/examples/03_knn_from_scratch.py`
- `machine-learning/examples/03_classification_clustering_demo.py`
- `machine-learning/examples/04_regression_svm_pca_demo.py`
- `machine-learning/examples/05_svm_kernel_demo.py`
- `machine-learning/examples/06_pca_dimensionality_demo.py`
- `machine-learning/examples/07_genetic_algorithm_binary.py`
- `machine-learning/examples/08_cannibals_missionaries_bfs.py`
- `deep-learning/class-code/docker-flask-basics/docker_command_quickstart.md`
- `deep-learning/class-code/flask-api-basic/api_server.py`
- `deep-learning/class-code/comfyui-basic/queue_prompt_demo.py`
- `deep-learning/class-code/local-llm/ollama_chat_demo.py`
- `deep-learning/class-code/local-llm/prompting_patterns.py`
- `deep-learning/class-code/langchain-basic/simple_chain_demo.py`
- `deep-learning/class-code/langchain-memory-basic/conversation_memory_demo.py`
- `deep-learning/class-code/langchain-memory-basic/sliding_window_memory_demo.py`
- `deep-learning/class-code/time-series/windowing_demo.py`

## 빠른 실행

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Lab 앱은 추가 패키지가 필요합니다.

```powershell
pip install -r lab/requirements.txt
```

## Docker

Docker는 루트에 모으지 않고 각 영역 안의 `docker/` 폴더로 분리했습니다.
`requirements.txt`는 실행 코드가 있는 폴더에 두고, Dockerfile과 compose 파일만 영역별
`docker/` 폴더에서 관리합니다.

```powershell
cd D:\ML_DL_Class\machine-learning\docker
docker compose up machine-learning

cd D:\ML_DL_Class\deep-learning\docker
docker compose up flask-api-basic

cd D:\ML_DL_Class\lab\docker
docker compose up dl1-mc-game
```

