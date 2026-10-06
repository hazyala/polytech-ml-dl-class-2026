# 머신러닝 과제 — 분류·군집·회귀·탐색

노트북 실험과 독립 Flask 앱을 모았다. 데이터 전처리, 모델 평가와 입력 데이터 구성에 따른 결과를 비교한다.

| 과제 | 작성한 내용 |
|---|---|
| [Iris KNN·KMeans·PCA](01-iris-knn-kmeans-pca/README.md) | 품종 분류, 군집/품종 대응, 원본·선택 feature·PCA 차원 비교 |
| [강 건너기 BFS](02-cannibals-missionaries.py) | 상태·이동·규칙을 표현하고 queue와 방문 상태로 풀이 탐색 |
| `03-kaggle-practice/` | 기대수명 CSV의 결측 제거·상관관계, 원본/정규화 입력의 LinearRegression과 MSE 비교 |
| [Flask 분류 화면](04-breast-cancer-flask/README.md) | 저장된 scaler·분류 모델에 form 입력을 연결 |

## 실행 환경

이 폴더에서 `python -m pip install -r requirements.txt`로 노트북 의존성을 설치한다. `python -m jupyter lab`을 시작하고 과제별 `.ipynb`를 위에서부터 실행한다. BFS는 `python 02-cannibals-missionaries.py`로 실행한다. Flask 앱은 하위 README의 환경을 사용한다.

Docker 노트북은 저장소 루트에서 `cd lab/docker` 후 `docker compose --profile examples up --build ml-assignments`로 시작하고 localhost:8891에서 연다.

기대수명 노트북은 소스에 지정된 외부 CSV를 읽는다. `kaggle2.py`는 앞서 만든 `X`·`y` 변수를 사용하는 비교 코드이며 단독 실행 entry가 아니다. 결과 plot·평가 표는 노트북 출력에서 확인한다.
