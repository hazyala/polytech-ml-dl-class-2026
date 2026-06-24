from sklearn.datasets import load_iris
from sklearn import cluster
import numpy as np

def kMeans(X, k):
    print("kMeans() 군집화 적용...")
    model = cluster.KMeans(n_clusters=k, random_state=42)
    model.fit(X)
    labels = model.predict(X)
    print("군집화 결과 labels =", labels)
    return labels

# 데이터 로드
iris = load_iris()
X = iris.data   # 4개 특성값만 사용 (target 제외)
y = iris.target

# k=3으로 군집화
labels = kMeans(X, k=3)

# 다시 레이블링: 각 군집에서 가장 많이 등장하는 실제 레이블로 매핑
new_label = np.zeros_like(labels)
for i in range(3):
    mask = labels == i
    # 해당 군집에 속한 샘플들의 실제 클래스 중 최빈값 찾기
    most_common = np.bincount(y[mask]).argmax()
    new_label[mask] = most_common

print("다시 레이블링 한 후의 new_labels =", new_label)

# 정확도 계산
accuracy = np.sum(new_label == y) / len(y)
print("iris 데이터의 군집화 정확도:", accuracy)