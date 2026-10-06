# Image Muse — 한국어 설명에서 이미지까지

한국어 장면 설명을 Ollama로 영어 이미지 프롬프트로 바꾼 뒤 ComfyUI workflow에 넣어 생성하는 Flask 앱.

## 생성 요청의 흐름

1. `POST /api/translate_only`가 한국어 입력을 Ollama `/api/chat`으로 보내 영어 prompt를 받는다.
2. `POST /api/generate`가 positive/negative prompt, 이미지 크기·steps·cfg·seed를 `workflows/workflow.json`에 반영한다.
3. ComfyUI `/prompt`에 workflow를 제출하고 `prompt_id`로 `/history/{prompt_id}`를 polling한다.
4. 완성된 파일의 `/view` URL을 브라우저에 전달한다. 화면은 번역 결과·실행 상태·이미지·최근 생성 기록을 보여준다.

`GET /api/health`는 Ollama 모델·ComfyUI 연결 정보를 반환한다. 서버는 모델과 checkpoint 목록을 읽어 실행 대상을 선택하고 번역 실패·workflow 거절·생성 timeout을 `AppError`의 code/message로 전달한다.

## 실행 조건

Ollama 서버·모델과 ComfyUI 서버·workflow에서 사용할 checkpoint가 필요하다. 이 폴더에서:

```bash
python -m pip install -r requirements.txt
OLLAMA_BASE_URL=http://localhost:11434 COMFYUI_BASE_URL=http://localhost:8188 PORT=5102 python app.py
```

`http://localhost:5102`에 접속한다. Windows는 같은 변수를 PowerShell `$env:`로 지정한다. `OLLAMA_MODEL`의 기본값은 `gemma4:e2b`다. Docker 서비스는 `dl2-comfyui-translate`이며 모델 파일은 별도로 준비한다.

`app.py`는 번역·생성 API, `static/js/app.js`는 요청과 화면 갱신, `templates/index.html`은 입력·결과 화면이다.

[구현·화면 기록](report/DL2_COMFYUI_TRANSLATE_REPORT.md) · [상세 API](../../../docs/API.md) · [ComfyUI 모델](../../../docs/COMFYUI_MODEL_DOWNLOAD.md)
