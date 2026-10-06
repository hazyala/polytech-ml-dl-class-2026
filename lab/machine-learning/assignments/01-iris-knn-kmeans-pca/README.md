# Iris 입력 구성과 모델 비교

scikit-learn Iris 데이터의 네 feature로 품종을 분류하고 군집화·차원 축소 결과를 비교한 세 노트북.

| 노트북 | 실험 |
|---|---|
| [01_iris_knn_classification](01_iris_knn_classification.ipynb) | 분포·상관관계 EDA, 표준화, KNN 분류와 confusion matrix·classification report |
| [02_iris_kmeans_clustering](02_iris_kmeans_clustering.ipynb) | 표준화한 입력의 elbow/inertia, KMeans 3개 군집, 군집별 다수 품종으로 label 대응 |
| [03_iris_knn_pca_comparison](03_iris_knn_pca_comparison.ipynb) | 4D 입력·선택한 2개 feature·PCA 2/3/4차원에서 같은 KNN 비교, 주성분 설명 분산과 산점도 |

Matplotlib·seaborn으로 분포·box plot·상관관계·군집/품종 산점도를 그린다. PCA 비교는 random_state=42와 stratified 7:3 분할을 사용한다. 이 노트북의 StandardScaler는 분할 전에 전체 데이터에 fit하고 PCA는 train에 fit한다. KMeans 품종 대응 평가는 군집을 만든 데이터와 같은 데이터로 계산한다.

상위 [과제 환경](../README.md)을 준비한 뒤 각 노트북을 cell 순서대로 실행한다. Iris는 `load_iris()`로 불러오므로 별도 CSV 경로를 설정하지 않는다. 수치와 그림은 각 노트북의 저장된 출력에 있다.
