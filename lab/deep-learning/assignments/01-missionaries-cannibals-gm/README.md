# 강 건너기 게임 — BFS 풀이와 LLM GM

선교사 3명과 식인종 3명을 강 건너편으로 옮기는 게임. 브라우저에서 수동 이동 또는 AI 턴을 선택하고 보트 애니메이션과 해설을 확인한다.

## 무엇을 구현했나

`game_engine.py`가 강 양쪽의 인원과 배 위치를 `Status`로 표현한다. 다섯 이동 command의 가능 여부, 이동 후 상태와 승리·실패를 계산한다. AI 턴에서는 BFS로 승리 경로의 다음 이동을 찾고, 경로를 못 찾으면 안전/유효 command 안에서 LLM이 선택한다. `llm_gm.py`는 Ollama와 LangChain으로 턴 결과를 한국어로 설명한다.

게임 규칙·상태 전이는 Python이, 해설은 LLM이 담당한다. `app.py`는 현재 상태·방문 상태·턴 이력을 Flask session에 저장하고 `static/js/game.js`가 응답을 화면에 반영한다.

| Method | Endpoint | 동작 |
|---|---|---|
| POST | `/api/start` | 초기 상태·가능 command 반환 |
| POST | `/api/ai_turn` | 다음 이동 선택, 판정·GM 해설 반환 |
| POST | `/api/manual_turn` | JSON `command` 번호로 한 턴 진행 |

## 실행

이 폴더에서 설치·실행한다. 별도 Ollama 서버와 모델이 필요하다.

```bash
python -m pip install -r requirements.txt
OLLAMA_BASE_URL=http://localhost:11434 PORT=5101 python app.py
```

`http://localhost:5101`에서 게임을 시작한다. POSIX shell 명령이며 Windows에서는 같은 변수를 PowerShell `$env:`로 지정한다. 모델은 `OLLAMA_MODEL`(기본 `gemma4:e2b`), session 서명 키는 `FLASK_SECRET_KEY`로 설정한다. Docker 서비스 이름은 `dl1-mc-game`이다.

[구성·규칙·화면 기록](report/DL1_AI_COLLAB_REPORT.md) · [상세 API](../../../docs/API.md) · [Docker](../../../docker/README.md)
