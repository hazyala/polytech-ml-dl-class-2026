# docker 환경 구축

## 1. docker 컨테이너 생성 
```
docker run -it -d -e DISPLAY=host.docker.internal:0.0 -v /tmp/.X11-unix:/tmp/.X11-unix -v d:\MachineLearning_Class:/workspace -p 3000:3000 --name ML python:3.12-slim /bin/bash
```

```
 docker exec -it ML /bin/bash
```

## 2. 패키지 설치
```
 apt update
```

```
 apt install -y python3-tk
```

```
 apt install -y dclock
 ```