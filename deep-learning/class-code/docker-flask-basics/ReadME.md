# Docker·WSL 환경과 Flask HTTP 실습

Docker 설치·컨테이너 명령과 WSL 환경을 정리하고, Flask로 URL routing과 HTTP method를 실습했다.

## 작성한 예제

| 파일 | 브라우저/HTTP 요청에 대한 동작 |
|---|---|
| `chapter02/flaskserver/hello.py` | `GET /`에 Hello World 반환 |
| `chapter02/flaskserver/oneroute.py` | `/`와 `/about`을 다른 함수로 처리 |
| `chapter02/flaskserver/multiroute.py` | `/`, `/index`, `/home`을 하나의 함수에 연결 |
| `chapter02/flaskserver/method.py` | `GET /`, `POST /submit`을 구분 |
| `chapter02/flaskserver/0514/` | Flask entry와 HTML template 예제 |

`chapter01/`에는 Docker 설치·명령, WSL 설정, Apache 웹 서버 실습과 HTML이 있다. `chapter02/`의 Markdown은 Flask와 컨테이너 구성·routing·method 설명이다.

## 실행

이 폴더에서 Python 환경에 `requirements.txt`를 설치한 뒤 예제 하나를 실행한다. 예제들이 같은 5000 포트를 사용하므로 하나씩 실행한다.

```bash
python -m pip install -r requirements.txt
python chapter02/flaskserver/hello.py
```

`http://localhost:5000`에서 응답을 확인한다. Docker 서비스는 저장소 루트에서 `cd deep-learning/docker` 후 `docker compose --profile examples up --build docker-flask-basics`로 시작하며 host 포트는 5004다. [Docker 구성](../../docker/README.md)
