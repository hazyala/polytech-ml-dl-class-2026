# Lab — 제출 과제와 텀프로젝트

수업 설명용 코드와 분리한 과제 산출물. 각 앱은 독립 Flask process이며 공통 API 서버로 합쳐진 구조가 아니다.

| 위치 | 내용 |
|---|---|
| [01-missionaries-cannibals-gm](deep-learning/assignments/01-missionaries-cannibals-gm/README.md) | 상태·유효 command·BFS와 LLM 해설을 연결한 게임 |
| [02-comfyui-translate-image](deep-learning/assignments/02-comfyui-translate-image/README.md) | 한글 설명 번역, ComfyUI workflow, history polling |
| [03-cookie-sse-chat](deep-learning/assignments/03-cookie-sse-chat/README.md) | session ID cookie, 메모리 history, SSE token 전송 |
| [chat-image-generator](deep-learning/term-projects/chat-image-generator/README.md) | 대화형 이미지 프롬프트와 생성 |
| [machine-learning 과제](machine-learning/assignments/README.md) | Iris KNN/KMeans/PCA, BFS, Kaggle, Flask 분류 실습 |
| [gas-leak-prediction](machine-learning/term-projects/gas-leak-prediction/README.md) | 센서 lag feature와 horizon별 선형회귀 |

## 실행 경계

`docker/docker-compose.yml`이 개별 서비스를 준비한다. dl1~term의 host port는 5101~5104이며 breast-cancer는 host 5001/container 5000이다. Ollama와 ComfyUI는 앱 외부 서버다. 전체 서비스를 켜도 필요한 모델·checkpoint가 자동 준비되는 것은 아니다.

[API 계약](docs/API.md) · [Docker 안내](docker/README.md) · [ComfyUI 모델 기록](docs/COMFYUI_MODEL_DOWNLOAD.md)

## 데이터와 기존 기록

`datasets/gas-leak-sample/`은 여섯 센서의 일부 실험 CSV와 이미지다. 원본 전체 데이터는 Git에 없고 `GAS_LEAK_DATASET_DIR`로 별도 지정한다. 센서별 파일 구성과 전체 데이터 지정 방법은 [dataset README](datasets/gas-leak-sample/README.md)에 있다.

[과제별 구현 기록](docs/PROJECT_DOCS.md)과 각 과제의 report에는 모델 연결·처리 흐름·화면이 있다. 개별 앱 README에서 실행을 시작한다. breast-cancer Flask는 학습 실험이고 실제 진단 시스템이 아니다.
