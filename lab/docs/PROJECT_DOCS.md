# Archived Original Docker/Lab Environment Document

This file preserves the original D:\ML_DL_Lab integrated Docker environment notes.
The current cleaned repository uses `lab/deep-learning`, `lab/machine-learning`,
`lab/datasets`, `lab/shared`, `lab/docs`, and `lab/docker`.
Use `lab/docker/docker-compose.yml` for the current Lab Docker entrypoint.
Paths below describe the old source layout and are kept only as migration notes.

# ML/DL 과제 통합 실습 환경 문서

## 1. 전체 구성 개요

### 환경 구성 목표
모든 과제를 **단일 Docker 컨테이너** 하나에서 실행한다.  
`supervisord`가 내부에서 여러 프로세스를 동시에 관리하는 방식이다.

### 시스템 구성도

```
Windows 호스트 (RTX 3080, WSL2)
│
├── ollama 컨테이너 (포트 11434)     ← 기존 컨테이너 재사용
│   └── gemma3:4b 모델 실행 중
│
└── ml_dl_lab 컨테이너 (신규)
    ├── ComfyUI          → 포트 8188
    ├── DL 과제1 Flask   → 포트 5101
    ├── DL 과제2 Flask   → 포트 5102
    ├── DL 과제3 Flask   → 포트 5103
    ├── DL 텀프로젝트    → 포트 5104  (미완성)
    └── Jupyter          → 포트 8888  (미완성)
```

Flask 앱들은 `host.docker.internal:11434` 로 ollama에 접근하고,  
ComfyUI는 동일 컨테이너 내부 `localhost:8188` 로 접근한다.

---

## 2. 폴더 구조

```
D:\ML_DL_Lab\
├── Dockerfile                        # 컨테이너 빌드 정의
├── docker-compose.yml                # 서비스 실행 정의
├── .env                              # 환경 변수 (Ollama URL, 모델명 등)
├── supervisor\
│   ├── supervisord.conf              # supervisor 메인 설정
│   └── apps.conf                     # 각 프로세스 실행 정의
├── apps\
│   ├── requirements.txt              # 전체 Python 패키지 목록
│   ├── common\
│   │   ├── ollama_client.py          # ChatOllama 공통 래퍼
│   │   └── comfyui_client.py         # ComfyUI API 공통 래퍼
│   ├── dl1_mc_game\                  # DL 과제1
│   ├── dl2_comfyui_translate\        # DL 과제2
│   ├── dl3_cookie_stream\            # DL 과제3
│   └── dl_term_chat_image\           # DL 텀프로젝트 (미완성)
├── comfyui_data\
│   ├── models\checkpoints\           # SD 체크포인트 모델 (볼륨 마운트)
│   ├── models\vae\
│   ├── models\loras\
│   ├── output\                       # 생성된 이미지 저장
│   └── input\
└── ml_term_gas\                      # ML 기초 텀프로젝트 (미완성)
    ├── data\
    ├── notebooks\
    ├── src\
    └── report\
```

---

## 3. Docker 구성

### Dockerfile 핵심 내용

| 단계 | 내용 |
|---|---|
| 베이스 이미지 | `nvidia/cuda:12.4.1-runtime-ubuntu22.04` |
| Python | 3.11 설치 + pip 최신화 |
| ComfyUI | `/opt` 에 git clone 후 의존성 설치 |
| PyTorch | CUDA 12.4 버전 (`--index-url https://download.pytorch.org/whl/cu124`) |
| Flask 앱 의존성 | `apps/requirements.txt` 기반 pip install |
| 앱 소스 | `/workspace/apps/` 로 복사 |
| 실행 | `supervisord` 로 전체 프로세스 관리 |

### docker-compose.yml 핵심 내용

```yaml
ports:
  - "8188:8188"   # ComfyUI
  - "5101:5101"   # DL 과제1
  - "5102:5102"   # DL 과제2
  - "5103:5103"   # DL 과제3
  - "5104:5104"   # DL 텀프로젝트
  - "8888:8888"   # Jupyter

volumes:
  - D:/ML_DL_Lab/comfyui_data/models:/opt/ComfyUI/models   # 모델 파일 영구 보존
  - D:/ML_DL_Lab/apps:/workspace/apps                       # 소스 실시간 반영

extra_hosts:
  - "host.docker.internal:host-gateway"                     # ollama 접근용
```

### supervisord 프로세스 관리

`supervisor/apps.conf` 에 정의된 프로세스 목록:

| 프로세스명 | 실행 명령 | 포트 | 우선순위 |
|---|---|---|---|
| `comfyui` | `python3 /opt/ComfyUI/main.py` | 8188 | 10 (가장 먼저) |
| `dl1_mc_game` | `python3 app.py` | 5101 | 20 |
| `dl2_comfyui_translate` | `python3 app.py` | 5102 | 20 |
| `dl3_cookie_stream` | `python3 app.py` | 5103 | 20 |
| `dl_term_chat_image` | `python3 app.py` | 5104 | 20 |
| `jupyter` | `python3 -m jupyter lab` | 8888 | 30 |

---

## 4. DL 과제1 - 식인종/선교사 LLM GM 웹앱

### 과제 요구사항
> LLM을 이용하여 식인종-선교사 게임을 진행하는 GM 또는 문제해결 AI협업 웹 프로그램을 작성하시오.

### 접속 URL
`http://localhost:5101`

### 폴더 구조
```
apps\dl1_mc_game\
├── app.py              # Flask 서버 (라우트 3개)
├── game_engine.py      # 게임 로직 (Status, game, judge)
├── llm_gm.py           # LLM GM (커맨드 자동 선택 + 해설)
├── templates\
│   └── index.html      # 픽셀 아트 게임 UI
└── static\
    ├── css\style.css   # Press Start 2P 픽셀 폰트 스타일
    └── js\game.js      # AI/수동 모드 UI 로직
```

### 동작 방식

```
[PPT 구조 그대로]
상태(Status) → 커맨드(Command) → 게임(Game) → 판정(Judge)

[AI 자동 모드]
현재 상태 → LLM(Ollama)이 커맨드 선택 → 게임 엔진 실행 → 결과 판정 → 화면 업데이트

[수동 모드]
사용자가 커맨드 버튼 클릭 → 게임 엔진 실행 → 결과 판정 → 화면 업데이트
```

### 파일별 역할

| 파일 | 역할 | PPT 대응 |
|---|---|---|
| `game_engine.py` | `Status` 클래스, `COMMANDS`, `game()`, `judge()`, `get_valid_commands()` | Chapter 7 PPT 구조 그대로 |
| `llm_gm.py` | `ChatOllama` + LCEL 체인으로 GM이 커맨드 선택, 해설 생성 | Chapter 4 Role-based Prompting |
| `app.py` | `/api/start`, `/api/ai_turn`, `/api/manual_turn` 라우트 | Chapter 2 Flask 라우팅 |
| `index.html` | 픽셀 아트 게임 화면, AI/수동 모드 버튼 | - |
| `game.js` | `fetch` API 호출, 말풍선/배/캐릭터 실시간 렌더링 | - |

### API 라우트

| 라우트 | 메서드 | 설명 |
|---|---|---|
| `/` | GET | 게임 메인 화면 |
| `/api/start` | POST | 게임 초기화, 초기 상태 반환 |
| `/api/ai_turn` | POST | LLM GM이 커맨드 선택 후 한 턴 진행 |
| `/api/manual_turn` | POST | 사용자 커맨드로 한 턴 진행 |

### 무한반복 방지 (PPT 문제 상황 반영)
- **문제 상황 1**: 이전 커맨드와 같은 커맨드 → 히스토리 기반 감지
- **문제 상황 2**: 이미 방문한 상태 재방문 → `visited` 리스트로 감지 후 대체 커맨드 선택

---

## 5. DL 과제2 - ComfyUI 한→영 번역 이미지 생성

### 과제 요구사항
> ComfyUI의 API를 이용하여 Local에서 한글로 작성된 프롬프트를 영문으로 자동 번역하여 이미지를 생성하는 웹 프로그램을 작성하시오.

### 접속 URL
`http://localhost:5102`

### 폴더 구조
```
apps\dl2_comfyui_translate\
├── app.py                    # Flask 서버
├── templates\
│   └── index.html            # 픽셀 아트 이미지 생성 UI
├── static\
│   ├── css\style.css
│   └── js\app.js             # 번역 미리보기, 이미지 생성, 히스토리
└── workflows\
    └── workflow.json         # ComfyUI SD1.5 기본 워크플로
```

### 동작 방식

```
한글 입력
   ↓
LLM(Ollama) 번역 → 영문 SD 프롬프트 생성
   ↓
POST /prompt → ComfyUI 큐 등록 (prompt_id 수신)
   ↓
poll_history() → GET /history/{prompt_id} 폴링 (완료 대기)
   ↓
extract_first_image_url() → 이미지 URL 추출
   ↓
브라우저에 이미지 표시 + 히스토리 썸네일 추가
```

### 파일별 역할

| 파일 | 역할 | PPT 대응 |
|---|---|---|
| `app.py` | `load_workflow`, `update_prompts`, `submit_prompt`, `poll_history`, `extract_first_image_url` | Chapter 3 app2.py 1~4/4 그대로 |
| `app.py` 번역 | `ChatOllama` LCEL 체인으로 한글→영문 SD 프롬프트 변환 | Chapter 4 과제 내용 |
| `workflows/workflow.json` | SD1.5 기본 워크플로 (노드6=positive, 노드7=negative) | Chapter 3 test.json 역할 |
| `app.js` | 번역 미리보기, 생성 요청, 흐름 단계 표시, 히스토리 관리 | - |

### API 라우트

| 라우트 | 메서드 | 설명 |
|---|---|---|
| `/` | GET | 이미지 생성 메인 화면 |
| `/api/generate` | POST | 한글입력 → 번역 → ComfyUI 생성 → 이미지 URL 반환 |
| `/api/translate_only` | POST | 번역 미리보기 (이미지 생성 없이 영문만 확인) |

### workflow.json 주의사항
기본 제공된 `workflow.json`은 SD1.5 구조이다.  
실제 사용 시 ComfyUI에서 본인 워크플로를 **API 포맷**으로 내보내서 교체해야 한다.  
(ComfyUI → 설정 → `Enable Dev mode Options` → `Save (API Format)`)

---

## 6. DL 과제3 - 쿠키 세션 + SSE 스트리밍 챗봇

### 과제 요구사항
> Cookie를 사용하여 브라우저가 닫혀도 세션을 복구하여 이전 대화가 지속되어야 하며, 사용자 요청에 의해 이전 대화 삭제 기능 구현, 최종 스트리밍 구현으로 채팅 웹 내 생성되는 텍스트를 실시간 표현하는 웹 프로그램을 작성하시오.

### 접속 URL
`http://localhost:5103`

### 폴더 구조
```
apps\dl3_cookie_stream\
├── app.py              # Flask 서버 (라우트 4개 + 쿠키 세션 + SSE)
├── templates\
│   └── index.html      # Jinja2 이전 대화 렌더링 + 픽셀 챗봇 UI
└── static\
    ├── css\style.css   # 픽셀 아트 챗봇 스타일
    └── js\chat.js      # fetch + ReadableStream SSE 수신
```

### 동작 방식

```
[최초 접속]
브라우저 → GET / → 쿠키에 session_id 없음
→ 새 UUID 생성 → 쿠키 set (max_age=7일)
→ 빈 대화 화면 렌더링

[재접속 (브라우저 닫혔다 열어도)]
브라우저 → GET / → 쿠키에서 session_id 읽기
→ chat_store[session_id] 에서 이전 대화 로드
→ Jinja2로 이전 대화 HTML 렌더링 (복구 완료)

[메시지 전송 + SSE 스트리밍]
사용자 입력 → POST /api/stream
→ chain.stream() 토큰 단위 생성
→ SSE "data: {token}\n\n" 형식으로 실시간 전송
→ chat.js ReadableStream으로 수신 → 말풍선에 토큰 추가

[대화 삭제]
삭제 버튼 클릭 → POST /api/clear
→ chat_store[session_id] = [] 초기화
→ 화면 초기화
```

### 파일별 역할

| 파일 | 역할 | PPT 대응 |
|---|---|---|
| `app.py` | 라우트 4개 + 쿠키 세션 + SSE 스트리밍 + 메모리 저장소 전부 포함 | - |
| `app.py` `/api/stream` | `stream_with_context`, `chain.stream()`, `_sse_format()`, SSE 헤더 | Chapter 5 app_sse.py 그대로 |
| `app.py` `chat_store` | `session_id` 키로 대화 기록 InMemory 저장 | Chapter 6 InMemory 방식 |
| `app.py` 쿠키 처리 | `get_or_create_session()` — `max_age=7일` 쿠키로 브라우저 닫혀도 복구 | 과제 요구사항 |
| `app.py` `/api/clear` | `chat_store[session_id] = []` 초기화 | 과제 요구사항 |
| `templates/index.html` | Jinja2 `{% for msg in history %}` 이전 대화 렌더링 | 과제 요구사항 |
| `static/css/style.css` | 픽셀 아트 챗봇 UI 스타일 | - |
| `static/js/chat.js` | `fetch` + `ReadableStream`으로 SSE 수신 → 토큰 단위 실시간 말풍선 출력 | - |

### API 라우트

| 라우트 | 메서드 | 설명 |
|---|---|---|
| `/` | GET | 메인 화면 + 쿠키로 이전 대화 복구 |
| `/api/stream` | POST | SSE 스트리밍 응답 |
| `/api/history` | GET | 현재 세션 대화 기록 조회 |
| `/api/clear` | POST | 이전 대화 전체 삭제 |

---

## 7. 공통 모듈

### lab/shared/apps-common/ollama_client.py

| 함수 | 설명 |
|---|---|
| `get_llm()` | `ChatOllama` 인스턴스 반환 |
| `build_conversation_chain()` | `ConversationBufferMemory` 기반 멀티턴 체인 |
| `build_lcel_chain()` | `prompt \| llm \| StrOutputParser` LCEL 파이프라인 |

### lab/shared/apps-common/comfyui_client.py

| 함수 | 설명 |
|---|---|
| `submit_prompt()` | `POST /prompt` 워크플로 큐 등록 → `prompt_id` 반환 |
| `wait_for_result()` | WebSocket으로 완료 감지 |
| `get_output_images()` | `GET /history/{prompt_id}` 이미지 파일명 추출 |
| `get_image_url()` | 이미지 접근 URL 생성 |
| `load_workflow()` | workflow JSON 파일 로드 |

---

## 8. 빌드 및 실행 방법

### 사전 준비
```powershell
# 1. Ollama 컨테이너 시작
docker start ollama
docker exec -it ollama ollama list

# 모델 없으면 pull
docker exec -it ollama ollama pull gemma3:4b
```

### 빌드 및 실행
```powershell
cd D:\ML_DL_Lab

# 빌드 (최초 1회, PyTorch + ComfyUI 설치로 10~20분 소요)
docker compose build

# 실행
docker compose up -d

# 상태 확인
docker exec -it ml_dl_lab supervisorctl status

# 개별 로그 확인
docker exec -it ml_dl_lab supervisorctl tail -f dl1_mc_game
docker exec -it ml_dl_lab supervisorctl tail -f dl3_cookie_stream
```

### 접속 URL

| 서비스 | URL | 상태 |
|---|---|---|
| DL 과제1 - 식인종/선교사 GM | http://localhost:5101 | ✅ 완성 |
| DL 과제2 - 한→영 이미지생성 | http://localhost:5102 | ✅ 완성 |
| DL 과제3 - 쿠키세션 + SSE | http://localhost:5103 | ✅ 완성 |
| DL 텀프로젝트 | http://localhost:5104 | 🔨 미완성 |
| ComfyUI | http://localhost:8188 | ✅ 완성 |
| Jupyter (ML 텀프로젝트) | http://localhost:8888 | 🔨 미완성 |

### ComfyUI 모델 다운로드
빌드 후 체크포인트 모델을 넣어야 이미지 생성이 가능하다.
```powershell
# 컨테이너 접속 후 모델 다운로드
docker exec -it ml_dl_lab bash
cd /opt/ComfyUI/models/checkpoints
wget -O v1-5-pruned-emaonly.safetensors \
  "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
```
또는 `D:\ML_DL_Lab\comfyui_data\models\checkpoints\` 에 직접 모델 파일을 복사해도 된다 (볼륨 마운트).

---

## 9. 미완성 항목 (진행 예정)

| 순서 | 과제 | 포트 | 내용 |
|---|---|---|---|
| 4 | DL 텀프로젝트 | 5104 | LangChain 0.3.17 + ComfyUI 대화형 이미지생성, [그림생성] 버튼 |
| 5 | ML기초 텀프로젝트 | 8888 | 가스환경 6개 입력 → 3/9/30/60/120초 후 예측 모델 + 보고서 |


