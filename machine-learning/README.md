# 머신러닝 수업 실습

NumPy·pandas로 데이터를 정리하고 KNN·회귀·SVM·PCA·군집화·탐색 알고리즘을 실습한 Python 코드와 노트북.

| 위치 | 내용 |
|---|---|
| [class-code](class-code/README.md) | 날짜별 수업 노트북과 챕터별 필기·예제 |
| `examples/` | 배열·거리 계산, 직접 작성한 KNN, 회귀·SVM·PCA 시각화, 유전 알고리즘, 강 건너기 BFS |
| [docker](docker/README.md) | 수업 폴더를 mount하는 JupyterLab 환경 |
| [과제](../lab/machine-learning/assignments/README.md) | Iris 비교 실험, BFS, 기대수명 회귀, Flask 분류 화면 |
| [가스 누출 예측](../lab/machine-learning/term-projects/gas-leak-prediction/README.md) | 센서 lag feature로 미래 누출량을 예측하는 텀프로젝트 |

## 코드 읽기·실행

이 폴더의 `requirements.txt`에 NumPy·pandas·scikit-learn·Matplotlib·Jupyter 의존성이 있다. 노트북은 위에서부터 cell 순서로 실행하고, `examples/`의 Python 파일은 개별 프로그램으로 실행한다.

저장소 루트에서 JupyterLab을 시작하려면:

```bash
cd machine-learning/docker
docker compose up --build machine-learning
```

`http://localhost:8888`에서 실습 노트북을 연다. 날짜별 코드와 과제는 각각의 데이터·실험 설정을 사용한다.
