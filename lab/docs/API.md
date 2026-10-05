# Lab Flask API 계약

각 앱의 app.py routing을 기준으로 정리했다. 같은 endpoint 이름이 있어도 서로 다른 process다. 별도 사용자 로그인·token 인증은 없으며 cookie/session은 상태 식별용이다. 아래 POST 본문은 별도 언급이 없으면 JSON이다.

## DL1 — 선교사·식인종 GM, 5101

| Method | Path | 입력 | 응답 |
|---|---|---|---|
| GET | `/` | 없음 | 게임 HTML |
| POST | `/api/start` | 없음 | status, valid_commands, command_names, turn=0 |
| POST | `/api/ai_turn` | session cookie | turn, command, cmd_name, status, result, comment, valid_commands |
| POST | `/api/manual_turn` | command 정수 + session cookie | 같은 턴 결과 |

start 전에 턴 요청은 400이다. 유효하지 않은 manual command도 400이다. Flask session에 status/history/visited/turn을 기록한다. AI 턴은 solution command 탐색을 먼저 사용하고 필요할 때 GM 선택을 사용하므로 모든 결정을 LLM이 한다고 설명하지 않는다.

## DL2 — 번역 이미지 생성, 5102

| Method | Path | 입력 | 응답 |
|---|---|---|---|
| GET | `/` | 없음 | HTML |
| GET | `/api/health` | 없음 | comfyui, ollama, workflow_exists/path, 연결 URL·model |
| POST | `/api/translate_only` | korean_input | eng_prompt |
| POST | `/api/generate` | korean_input; neg_prompt, width, height, steps, cfg(선택) | korean_input, eng_prompt, neg_prompt, img_url, prompt_id, settings |

크기 기본 512×512, steps=20, cfg=7. 빈 입력은 400, AppError는 code/error와 자체 status, 예상 밖 예외는 500이다. LLM 번역 후 ComfyUI workflow를 제출하고 history polling으로 결과를 찾는다.

## DL3 — Cookie + SSE chat, 5103

| Method | Path | 입력 | 응답 |
|---|---|---|---|
| GET | `/` | cookie(선택) | HTML + session ID cookie |
| GET | `/api/status` | cookie | status, session_id, model, base_url, history_count, cookie_name |
| GET | `/api/history` | cookie | session_id, history |
| POST | `/api/clear` | cookie | status=ok, message |
| POST | `/api/stream` | message + cookie | text/event-stream |

SSE event는 open(status/model), token(text), error(code/message), end(status/chars)다. 빈 message는 스트림 전 JSON 400이다. 스트리밍 실패는 HTTP 연결 안의 error event라 상태코드만으로 성공을 판단하지 않는다. 이력은 서버 메모리 dict에 있어 재시작 후 사라진다.

## Prompt Canvas — 5104

| Method | Path | 입력 | 응답 |
|---|---|---|---|
| GET | `/` | cookie(선택) | HTML + session ID cookie |
| GET | `/api/status` | cookie | session_id, model, current_prompt, message_count, image_count, comfyui, ollama |
| POST | `/api/chat` | message + cookie | reply, current_prompt, model, messages |
| POST | `/api/generate` | prompt(선택); negative_prompt, width, height, steps, cfg | prompt_id, image_url, prompt, negative_prompt, settings |
| GET | `/api/comfyui/view` | query filename 필수, subfolder, type=output | 이미지 bytes / upstream Content-Type |
| POST | `/api/clear` | cookie | status=ok |

prompt 생략 시 session의 current_prompt를 사용한다. 기본 크기 512×512, steps=20, cfg=7. 빈 message/prompt/filename은 400, chat 실패·image proxy 실패는 502, AppError는 지정 status와 code/message, 예상 밖 generate 오류는 500이다. cookie는 사용자 인증을 대신하지 않는다.

## ML Flask 분류 과제 — host 5001

`machine-learning/assignments/04-breast-cancer-flask/app.py`: GET `/`는 HTML, POST `/predict`는 form v1/v2를 float로 읽어 30개 feature 중 나머지를 0으로 채우고 scaler·model을 호출한다. 응답은 결과 또는 오류가 담긴 HTML이다. 실제 진단 API로 안내하지 않는다.

## 수업용 독립 API

[flask-api-basic/api_server.py](../../deep-learning/class-code/flask-api-basic/api_server.py)는 기본 5000에서 GET `/`(message), GET `/api/echo`(query text), POST `/api/echo`(JSON text, payload), POST `/api/predict`(JSON values 숫자 배열 → 평균 prediction)를 제공한다. 숫자 배열 오류는 400이고 빈 배열 평균은 0이다. ML 모델 추론 endpoint가 아니다.

LangChain 수업의 [flask_chain.py](../../deep-learning/class-code/langchain-basic/flask_chain.py)는 POST `/summarize`, [json.py](../../deep-learning/class-code/langchain-basic/json.py)는 POST `/summarize/structured`, [app_see.py](../../deep-learning/class-code/langchain-basic/app_see.py)는 POST `/summarize/stream`을 선언한다. text 입력과 요약 응답을 다루는 강의 코드이며 첫 파일의 `request.get_json()(silent=True)` 호출 오류 등 실행 전 보완이 필요한 코드가 포함되어 있다. 스트림의 Content-Type도 text/plain이므로 Lab SSE 계약과 혼동하지 않는다.

## source

[DL1](../deep-learning/assignments/01-missionaries-cannibals-gm/app.py) · [DL2](../deep-learning/assignments/02-comfyui-translate-image/app.py) · [DL3](../deep-learning/assignments/03-cookie-sse-chat/app.py) · [Prompt Canvas](../deep-learning/term-projects/chat-image-generator/app.py) · [compose 포트](../docker/docker-compose.yml)
