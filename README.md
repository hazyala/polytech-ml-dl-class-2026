# ML/DL 실습과 과제 pipeline

머신러닝 수업 코드, LLM·ComfyUI 웹 실습, 가스 누출 예측과 대화형 이미지 생성 과제를 모은 저장소.

## 먼저 볼 산출물

| 프로젝트 | 구현 |
|---|---|
| [가스 누출 예측](lab/machine-learning/term-projects/gas-leak-prediction/README.md) | 센서 CSV 병합·lag feature → StandardScaler → LinearRegression, 시간 horizon별 평가 |
| [Prompt Canvas](lab/deep-learning/term-projects/chat-image-generator/README.md) | 대화로 이미지 프롬프트 갱신 → ComfyUI workflow 실행 → 결과 이미지 |
| [Lab 과제](lab/README.md) | LLM GM 게임, 한영 번역 이미지 생성, cookie+SSE 채팅, ML 과제 |

수업 저장소이므로 과제·실험 결과와 서비스 운영 성과를 구분한다. 모델 정확도나 성공률을 새 측정치처럼 요약하지 않고 기존 report와 실제 평가 코드를 연결한다.

## 자료 구성

- `machine-learning/class-code/`: 날짜별 노트북, 챕터 필기·예제
- `machine-learning/examples/`: NumPy/Pandas, KNN, 회귀·SVM·PCA, 유전 알고리즘, BFS 진입 예제
- `deep-learning/class-code/`: Flask, Ollama, LangChain, ComfyUI, 시계열 예제
- `lab/`: 제출 과제·텀프로젝트·샘플 dataset·기존 보고서
- 각 영역의 `docker/`: 영역별 Dockerfile·compose·실행 안내

## 작은 예제로 시작

Python 가상환경에서 root 의존성을 설치한다. 별도의 Python runtime lock은 없으므로 각 과제의 고정 requirements와 구분한다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python machine-learning/examples/03_knn_from_scratch.py
```

Windows 활성화는 `.venv\Scripts\Activate.ps1`을 사용한다. root requirements가 모든 Lab의 모델·외부 서버·패키지까지 준비하는 것은 아니다. 웹앱과 텀프로젝트는 해당 README와 requirements를 따른다.

Docker 실행은 저장소 경로를 기준으로 한다.

```bash
cd lab/docker
docker compose up --build dl3-cookie-sse-chat
```

Ollama 서버와 모델은 별도 준비가 필요하다. 각 compose의 host.docker.internal 연결과 포트를 확인한다. [Lab Docker](lab/docker/README.md), [ML Docker](machine-learning/docker/README.md), [DL Docker](deep-learning/docker/README.md)에 기존 환경 기록이 있다.

[Lab API](lab/docs/API.md)에는 실제 routing 입력·응답을 정리했다. 단순 Flask 수업 예제는 소스 링크와 함께 별도 목록에 구분했다. [과제별 구현 기록](lab/docs/PROJECT_DOCS.md)에는 과제 구성과 코드 설명이 있다.
