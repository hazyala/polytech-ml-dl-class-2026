C:\Users\AISW-509-IP>docker --version
Docker version 29.3.0, build 5927d80

C:\Users\AISW-509-IP>docker ps
CONTAINER ID   IMAGE                              COMMAND               CREATED         STATUS          PORTS                                             NAMES
1d2670b70fb5   ollama/ollama                      "/bin/ollama serve"   6 minutes ago   Up 6 minutes    0.0.0.0:11434->11434/tcp, [::]:11434->11434/tcp   ollama
705109f436d4   python:3.12-slim                   "python3"             3 weeks ago     Up 17 minutes   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp       flaskserver
48a604860eb5   tensorflow/tensorflow:2.16.2-gpu   "/bin/bash"           5 weeks ago     Up 26 minutes                                                     tensorflow

C:\Users\AISW-509-IP>docker exec -it ollama ollama list
NAME    ID    SIZE    MODIFIED

C:\Users\AISW-509-IP>docker exec -it ollama ollama run gemma4:e2b
pulling manifest
pulling 4e30e2665218: 100% ▕██████████████████████████████████████████████████████████▏ 7.2 GB
pulling 7339fa418c9a: 100% ▕██████████████████████████████████████████████████████████▏  11 KB
pulling 56380ca2ab89: 100% ▕██████████████████████████████████████████████████████████▏   42 B
pulling c6bc3775a3fa: 100% ▕██████████████████████████████████████████████████████████▏  473 B
verifying sha256 digest
writing manifest
success