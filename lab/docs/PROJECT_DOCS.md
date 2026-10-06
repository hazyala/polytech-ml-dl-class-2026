# ML/DL 과제 구현 지도

독립 Flask 앱 네 개와 머신러닝 노트북·센서 예측 실험을 만들었다. 웹앱은 브라우저 입력을 모델 호출과 연결하고, 노트북은 데이터 전처리·학습·평가를 기록한다.

## 웹 과제에서 만든 것

| 프로젝트 | 입력 → 처리 → 결과 |
|---|---|
| [강 건너기 GM](../deep-learning/assignments/01-missionaries-cannibals-gm/README.md) | 수동/AI 턴 → 유효 이동·BFS·승패 판정 → 보트 이동과 Ollama 해설 |
| [Image Muse](../deep-learning/assignments/02-comfyui-translate-image/README.md) | 한국어 장면 → 영어 prompt 번역·ComfyUI workflow → 생성 이미지 |
| [쿠키·SSE 채팅](../deep-learning/assignments/03-cookie-sse-chat/README.md) | 대화 입력 → session ID별 history·LangChain stream → token event 말풍선 |
| [Prompt Canvas](../deep-learning/term-projects/chat-image-generator/README.md) | 대화로 장면 수정 → FINAL_PROMPT 추출·workflow 생성 → 이미지 proxy·이력 |

### 규칙과 LLM 역할 분리

강 건너기의 이동 가능 여부·상태 전이·승패는 `game_engine.py`가 계산한다. AI 턴은 BFS 경로를 우선 사용하고 LLM은 턴 해설과 fallback command 선택을 담당한다. Flask session은 상태·방문 목록·턴 기록을 보관한다.

### 번역과 이미지 생성 연결

Image Muse는 Ollama 번역 결과를 ComfyUI graph의 prompt node에 넣고 크기·steps·cfg·seed를 반영한다. `/prompt` 제출 → `/history` polling → `/view` 결과 표시 순서다. Prompt Canvas는 대화로 영어 prompt를 계속 다듬고 생성 요청을 별도 API로 보낸다. 두 앱 모두 ComfyUI와 checkpoint는 외부에 준비한다.

### 대화 ID와 저장 위치

SSE 채팅과 Prompt Canvas는 쿠키에 ID를 넣고 서버 메모리 dict에서 대화 또는 생성 이력을 찾는다. 브라우저 재접속은 같은 쿠키로 이력을 읽으며 서버 재시작 후 이력은 사라진다. SSE 과제는 `open/token/error/end` event를 전송하고 Prompt Canvas의 채팅은 전체 JSON을 반환한다.

## 머신러닝 실험

[과제 폴더](../machine-learning/assignments/README.md)에는 Iris KNN·KMeans·PCA 비교, 강 건너기 BFS, 기대수명 회귀와 저장 모델을 읽는 Flask 추론 화면이 있다.

[가스 누출 예측](../machine-learning/term-projects/gas-leak-prediction/README.md)은 여섯 센서의 time/value CSV를 실험 ID·시각으로 병합한다. 현재·lag 값으로 feature를 만들고 3·9·30·60·120초 뒤 누출량을 target으로 shift한다. 행 단위 random split 후 train에 scaler를 fit하고 horizon별 LinearRegression을 학습한다. MSE·MAE·RMSE·R²와 plot, joblib bundle을 파일로 저장한다.

## 실행 환경

[Docker compose](../docker/docker-compose.yml)는 앱마다 별도 서비스·working directory·requirements를 사용한다. 웹 과제 host 포트는 5101~5104, ML 노트북은 8891, 센서 텀프로젝트 노트북은 8889다. 분류 Flask 앱은 host 5001이다. Ollama·ComfyUI와 각 모델은 해당 앱 README의 설정으로 연결한다.

```bash
cd lab/docker
docker compose up --build dl1-mc-game
```

저장소 루트 기준이며 다른 앱은 service 이름을 선택한다. [Docker 서비스 목록](../docker/README.md) · [API 요청·응답](API.md) · [ComfyUI 모델 준비](COMFYUI_MODEL_DOWNLOAD.md)

`shared/apps-common/`에는 Ollama·ComfyUI client 실습 코드가 있다. 과제 app의 처리 흐름은 해당 `app.py`에서 시작한다.

## 구현·화면 기록

- [강 건너기 규칙·GM·화면](../deep-learning/assignments/01-missionaries-cannibals-gm/report/DL1_AI_COLLAB_REPORT.md)
- [번역 prompt·workflow·결과 화면](../deep-learning/assignments/02-comfyui-translate-image/report/DL2_COMFYUI_TRANSLATE_REPORT.md)
- [쿠키·SSE 코드·대화 복구 화면](../deep-learning/assignments/03-cookie-sse-chat/report/DL3_COOKIE_STREAM_REPORT.md)
- [Prompt Canvas](../deep-learning/term-projects/chat-image-generator/report/IMPLEMENTATION.md)
- [센서 모델·평가 기록](../machine-learning/term-projects/gas-leak-prediction/report/implementation_notes.md)
