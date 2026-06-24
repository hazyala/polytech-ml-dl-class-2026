# Lab Docker

과제와 텀프로젝트 앱을 실행하기 위한 Docker 구성입니다.

```powershell
cd D:\ML_DL_Class\lab\docker
docker compose up dl1-mc-game
docker compose up ml-gas-term
```

서비스:

| Service | Purpose | URL |
| --- | --- | --- |
| `ml-gas-term` | 가스 누출 예측 텀프로젝트 JupyterLab | <http://localhost:8889> |
| `ml-breast-cancer-flask` | 유방암 분류 Flask 과제 | <http://localhost:5001> |
| `dl1-mc-game` | 선교사-식인종 AI GM 과제 | <http://localhost:5101> |
| `dl2-comfyui-translate` | ComfyUI 이미지 번역 과제 | <http://localhost:5102> |
| `dl3-cookie-sse-chat` | 쿠키/SSE 채팅 과제 | <http://localhost:5103> |
| `dl-term-chat-image` | 채팅 이미지 생성 텀프로젝트 | <http://localhost:5104> |
| `ml-assignments` | ML 과제 노트북용 JupyterLab | <http://localhost:8891> |

Ollama를 Docker로 같이 띄우려면:

```powershell
docker compose --profile llm up ollama
```
