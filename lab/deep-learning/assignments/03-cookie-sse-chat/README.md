# 쿠키로 대화를 찾고 SSE로 답변을 보내는 챗봇

Flask가 대화 이력을 서버 메모리에 저장하고 Ollama 응답을 token event로 브라우저에 전달하는 채팅 과제.

## 세션과 스트리밍

브라우저 쿠키 `dl3_session_id`는 대화 ID를 보관한다. Flask의 `chat_store`가 ID별 메시지를 관리하며, 같은 쿠키로 다시 접속하면 대화 목록을 읽는다. 데이터는 Python process 메모리에 있으므로 서버를 재시작하면 사라진다.

`POST /api/stream`은 LangChain `chain.stream()`을 호출하고 `open` → `token` → `end` SSE 이벤트를 전송한다. 모델 호출 오류는 `error` event로 보낸다. `static/js/app.js`가 응답 스트림을 파싱해 말풍선을 갱신한다. `GET /api/history`는 이력 조회, `POST /api/clear`는 대화 초기화, `GET /api/status`는 모델·세션 상태 조회다.

## 실행

별도 Ollama 서버와 모델을 준비하고 이 폴더에서 실행한다.

```bash
python -m pip install -r requirements.txt
OLLAMA_BASE_URL=http://localhost:11434 PORT=5103 python app.py
```

`http://localhost:5103`에 접속한다. Windows는 같은 변수를 PowerShell `$env:`로 지정한다. `OLLAMA_MODEL`은 기본 `gemma4:e2b`, `FLASK_SECRET_KEY`는 Flask 설정 키다. Docker 서비스는 `dl3-cookie-sse-chat`이다.

[쿠키·SSE 코드와 화면 기록](report/DL3_COOKIE_STREAM_REPORT.md) · [API 이벤트](../../../docs/API.md) · [Docker](../../../docker/README.md)
