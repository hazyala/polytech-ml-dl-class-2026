# Deep Learning Docker

딥러닝 수업 코드용 Docker 구성입니다.

```powershell
cd D:\ML_DL_Class\deep-learning\docker
docker compose up flask-api-basic
docker compose --profile examples up langchain-basic
```

서비스:

| Service | Purpose | URL |
| --- | --- | --- |
| `flask-api-basic` | Python Flask API 기본 예제 | <http://localhost:5000> |
| `time-series` | 시계열 딥러닝 JupyterLab | <http://localhost:8890> |
| `docker-flask-basics` | Docker/Flask 기본 수업 예제 | <http://localhost:5004> |
| `flask-web-0422` | Flask 웹 예제 | <http://localhost:5003> |
| `local-llm-examples` | Ollama API CLI 예제 | command-line |
| `langchain-basic` | LangChain 기본 예제 | command-line |
| `langchain-memory-basic` | LangChain memory 예제 | command-line |
| `comfyui-basic` | ComfyUI API 예제 | command-line |

`examples` profile 서비스는 필요할 때만 실행합니다.
