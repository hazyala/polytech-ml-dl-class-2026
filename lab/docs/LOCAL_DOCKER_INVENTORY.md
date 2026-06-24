# Local Docker Inventory

이 문서는 2026-06-24 기준 로컬 Docker 환경을 정리한 참고 자료입니다.
Docker는 사용자가 입력한 원본 `docker run` 명령어를 완전히 저장하지 않으므로,
아래 명령어는 `docker inspect`, Compose labels, mounts, ports, image metadata를
기준으로 복원한 추정 예시입니다.

## 확인에 사용한 명령어

```powershell
docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}"
docker volume ls
docker network ls
docker inspect <container-name>
docker history --no-trunc <image-name>
```

## 현재 컨테이너 요약

| Container | Image | Status at check | Purpose / Source |
| --- | --- | --- | --- |
| `ml_dl_lab` | `ml_dl_lab-ml_dl_lab` | running | `D:\ML_DL_Lab` 통합 Lab Compose 환경 |
| `ollama` | `ollama/ollama` | exited | Ollama 서버 |
| `tensorflow` | `tensorflow/tensorflow:2.16.2-gpu` | exited | `D:\DeepLearning_Class2` GPU TensorFlow 실습 |
| `langapp` | `python:3.12-slim` | exited | `D:\DeepLearning_Class3` LangChain/LLM 실습 추정 |
| `flaskserver` | `python:3.12-slim` | exited | `D:\DeepLearning_Class\chapter02\flaskserver` Flask 실습 |
| `Flask` | `python:3.12-slim` | exited | `D:\FlaskWeb` Flask 웹 실습 |
| `myweb` | `httpd:latest` | exited | `D:\DeepLearning_Class` Apache/httpd 실습 |
| `ML` | `python:3.12-slim` | exited | `D:\MachineLearning_Class` ML 실습 |

## 생성 명령어 추정

### `ml_dl_lab`

Compose label에 원본 경로가 남아 있어 이 컨테이너는 Compose 생성으로 확정됩니다.

```text
D:\ML_DL_Lab\docker-compose.yml
```

추정 명령어:

```powershell
cd D:\ML_DL_Lab
docker compose up -d --build
```

또는 이미지가 이미 빌드된 뒤에는:

```powershell
cd D:\ML_DL_Lab
docker compose up -d
```

관련 포트:

```text
5101-5104 -> DL 과제/텀프로젝트 Flask 앱
8188      -> ComfyUI
8888      -> Jupyter
```

관련 마운트:

```text
D:\ML_DL_Lab:/workspace
D:\ML_DL_Lab\comfyui_data\models:/opt/ComfyUI/models
D:\ML_DL_Lab\comfyui_data\output:/opt/ComfyUI/output
D:\ML_DL_Lab\comfyui_data\input:/opt/ComfyUI/input
D:\ML_DL_Lab\supervisor\supervisord.conf:/etc/supervisor/supervisord.conf
D:\ML_DL_Lab\supervisor\apps.conf:/etc/supervisor/conf.d/apps.conf
```

### `ollama`

추정 명령어:

```powershell
docker run -d --name ollama `
  -p 11434:11434 `
  -v ollama:/root/.ollama `
  ollama/ollama
```

주의: `ollama` volume에는 내려받은 모델이 들어 있을 수 있습니다.
모델을 보존하려면 volume 삭제 전에 백업하거나 삭제하지 마세요.

### `tensorflow`

추정 명령어:

```powershell
docker run -it --name tensorflow `
  --gpus all `
  -p 80:5000 `
  -v D:\DeepLearning_Class2:/workspace `
  -v /tmp/.X11-unix:/tmp/.X11-unix `
  tensorflow/tensorflow:2.16.2-gpu `
  /bin/bash
```

### `langapp`

추정 명령어:

```powershell
docker run -it --name langapp `
  -p 5002:5000 `
  -v D:\DeepLearning_Class3:/workspace `
  python:3.12-slim `
  /bin/bash
```

### `flaskserver`

추정 명령어:

```powershell
docker run -it --name flaskserver `
  -p 5000:5000 `
  -v D:\DeepLearning_Class\chapter02\flaskserver:/workspace `
  python:3.12-slim `
  python3
```

### `Flask`

추정 명령어:

```powershell
docker run -it --name Flask `
  -p 82:5000 `
  -v D:\FlaskWeb:/workspace `
  -v /tmp/.X11-unix:/tmp/.X11-unix `
  python:3.12-slim `
  /bin/bash
```

### `myweb`

추정 명령어:

```powershell
docker run -d --name myweb `
  -p 1234:80 `
  -v D:\DeepLearning_Class:/usr/local/apache2/htdocs `
  httpd:latest
```

### `ML`

추정 명령어:

```powershell
docker run -it --name ML `
  -p 3000:3000 `
  -v D:\MachineLearning_Class:/workspace `
  -v /tmp/.X11-unix:/tmp/.X11-unix `
  python:3.12-slim `
  /bin/bash
```

## 이미지 요약

| Image | Size at check | Note |
| --- | ---: | --- |
| `ml_dl_lab-ml_dl_lab:latest` | 15.6GB | ComfyUI, PyTorch CUDA, Flask 앱 통합 이미지 |
| `ollama/ollama:latest` | 10.6GB | Ollama 서버 |
| `tensorflow/tensorflow:2.16.2-gpu` | 11.3GB | TensorFlow GPU 실습 |
| `python:3.12-slim` | 179MB | 여러 실습 컨테이너 공통 베이스 |
| `httpd:latest` | 177MB | Apache/httpd 실습 |
| `mariadb:latest` | 467MB | 현재 컨테이너 없음 |
| `nvidia/cuda:12.4.0-base-ubuntu22.04` | 348MB | CUDA 베이스 이미지 |
| `alpine:3.16.3` | 9.01MB | 현재 컨테이너 없음 |

## 삭제 명령어 예시

아래는 예시입니다. 실행 전 필요한 데이터와 Ollama 모델 보존 여부를 먼저 확인하세요.

### 컨테이너 중지

```powershell
docker stop ml_dl_lab ollama tensorflow langapp flaskserver Flask myweb ML
```

### 컨테이너 삭제

```powershell
docker rm ml_dl_lab ollama tensorflow langapp flaskserver Flask myweb ML
```

### 이미지 삭제

```powershell
docker rmi ml_dl_lab-ml_dl_lab:latest
docker rmi ollama/ollama:latest
docker rmi tensorflow/tensorflow:2.16.2-gpu
docker rmi python:3.12-slim
docker rmi httpd:latest
docker rmi mariadb:latest
docker rmi nvidia/cuda:12.4.0-base-ubuntu22.04
docker rmi alpine:3.16.3
```

### 볼륨 확인과 삭제

```powershell
docker volume ls
docker volume inspect ollama
```

Ollama 모델까지 삭제해도 되는 경우:

```powershell
docker volume rm ollama
```

익명 볼륨까지 정리하려면:

```powershell
docker volume prune
```

### 네트워크 정리

```powershell
docker network rm ml_dl_lab_default
```

사용하지 않는 Docker 리소스를 한 번에 정리하려면:

```powershell
docker system prune
```

이미지까지 포함해 크게 정리하려면:

```powershell
docker system prune -a
```

주의: `docker system prune -a`는 현재 컨테이너가 쓰지 않는 이미지를 광범위하게 삭제합니다.
