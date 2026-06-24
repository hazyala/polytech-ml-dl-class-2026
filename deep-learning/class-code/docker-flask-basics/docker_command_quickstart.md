# Docker Command Quickstart

Docker 강의자료를 보고 바로 따라칠 수 있는 최소 명령 모음입니다.

## Container Basics

```powershell
docker --version
docker images
docker ps
docker ps -a
```

## Run A Simple Web Server

```powershell
docker run --name class-httpd -p 8080:80 -d httpd:latest
docker logs class-httpd
docker stop class-httpd
docker rm class-httpd
```

## Python Container For Class Work

```powershell
docker run --name ml-python -it -v ${PWD}:/workspace -w /workspace python:3.12-slim bash
python --version
exit
```

## Cleanup

```powershell
docker container prune
docker image prune
```

Final course Dockerfiles should be rebuilt after the folder layout is fully settled.

