## 전체 구조 요약

```
머신러닝 파이썬 생태계
│
├── 수치 계산         → numpy
├── 데이터 처리       → pandas
├── 시각화 (기본)     → matplotlib
├── 시각화 (고급)     → seaborn
└── 머신러닝 모델     → scikit-learn  ← 이 강의의 핵심
```

---

## 1. NumPy (Numerical Python)

### 개념
- 파이썬 과학 계산의 **기반 라이브러리**
- 핵심 자료구조: `ndarray` (N차원 배열)
- C언어 기반 → 순수 파이썬보다 **수십~수백 배 빠름**
- 거의 모든 머신러닝 라이브러리가 내부적으로 NumPy 사용

### 왜 머신러닝에서 중요한가?
머신러닝에서 **데이터는 모두 숫자 행렬(행렬/벡터)** 로 표현된다.
- 입력 데이터 X → (n_samples, n_features) 2D 배열
- 가중치 w → 1D 벡터
- 예측값 → 1D 벡터
→ 이 모든 것을 NumPy `ndarray`로 처리

### 핵심 개념

| 개념 | 설명 | 예 |
|------|------|----|
| ndarray | N차원 배열 | `np.array([1,2,3])` |
| shape | 배열의 차원 크기 | `(3,)`, `(3,4)`, `(2,3,4)` |
| dtype | 데이터 타입 | `float64`, `int32`, `bool` |
| axis | 연산 방향 | axis=0: 행방향, axis=1: 열방향 |
| broadcast | 다른 shape 간 자동 연산 | `(3,1) + (1,4)` → `(3,4)` |

### 주요 기능 카테고리

#### 1) 배열 생성
```python
np.array([1, 2, 3])          # 리스트 → 배열
np.zeros((3, 4))             # 0으로 채운 3×4 배열
np.ones((2, 3))              # 1로 채운 2×3 배열
np.arange(0, 10, 2)         # [0, 2, 4, 6, 8]
np.linspace(0, 1, 5)        # [0, 0.25, 0.5, 0.75, 1.0]
np.random.randn(3, 4)       # 정규분포 난수 3×4
np.eye(3)                    # 단위행렬 (Identity Matrix)
```

#### 2) 인덱싱 & 슬라이싱
```python
a = np.array([[1,2,3],[4,5,6]])
a[0, 1]          # 1행 2열 → 2
a[:, 1]          # 전체 행, 2열 → [2, 5]
a[a > 3]         # 불리언 인덱싱 → [4, 5, 6]
```

#### 3) 수학 연산
```python
np.dot(A, B)     # 행렬 곱 (내적)
A @ B            # 행렬 곱 (파이썬 3.5+)
np.sum(a, axis=0)  # 열 방향 합계
np.mean(a)       # 평균
np.std(a)        # 표준편차
np.linalg.inv(A) # 역행렬
np.linalg.eig(A) # 고유값/고유벡터
```

#### 4) 형태 변환
```python
a.reshape(4, 3)    # 형태 변경 (원소 수 유지)
a.flatten()        # 1차원으로 펼치기
a.T                # 전치행렬
np.concatenate([a, b], axis=0)  # 배열 연결
np.stack([a, b])   # 새 차원으로 쌓기
```

### 머신러닝 연관성
- 선형대수 연산 → 선형회귀, PCA, SVM 내부 계산
- 난수 생성 → 가중치 초기화, 데이터 셔플
- 브로드캐스팅 → 배치 데이터 효율적 처리

---

## 2. Pandas

### 개념
- **테이블형 데이터 처리** 전문 라이브러리
- 핵심 자료구조: `Series`(1D), `DataFrame`(2D)
- R의 data.frame에서 영감 → 데이터 분석 문법 제공
- 내부적으로 NumPy 기반

### 왜 머신러닝에서 중요한가?
실제 ML 프로젝트에서 데이터는 CSV, Excel, DB 등에서 온다.
- 데이터 **로드 → 탐색 → 전처리 → 피처 엔지니어링** 전 과정
- 결측값 처리, 카테고리 인코딩, 데이터 분할 등

### 핵심 자료구조

#### Series (1차원)
```python
s = pd.Series([10, 20, 30], index=['a', 'b', 'c'])
# a    10
# b    20
# c    30
# dtype: int64
```

#### DataFrame (2차원 테이블)
```python
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Carol'],
    'age':  [25, 30, 22],
    'score': [85.0, 90.5, 78.3]
})
```

### 주요 기능 카테고리

#### 1) 데이터 로드
```python
pd.read_csv('data.csv')

pd.read_excel('data.xlsx')
pd.read_json('data.json')
pd.read_sql(query, conn)
```

#### 2) 탐색 (EDA 필수)
```python
df.head(5)          # 상위 5행
df.tail(5)          # 하위 5행
df.info()           # 컬럼 타입, null 개수
df.describe()       # 수치형 통계 요약
df.shape            # (행수, 열수)
df.dtypes           # 각 컬럼 데이터 타입
df['col'].value_counts()  # 빈도 분석
```

#### 3) 선택 & 필터링
```python
df['age']                      # 단일 컬럼 (Series)
df[['name', 'age']]            # 다중 컬럼 (DataFrame)
df.loc[0:2, 'name':'age']      # 레이블 기반 슬라이싱
df.iloc[0:3, 1:3]              # 위치 기반 슬라이싱
df[df['age'] > 25]             # 조건 필터링
df.query('age > 25 and score > 80')  # 쿼리 문법
```

#### 4) 전처리 (ML 필수)
```python
df.isnull().sum()              # 결측값 개수
df.fillna(0)                   # 결측값 → 0으로 대체
df.fillna(df.mean())           # 결측값 → 평균으로 대체
df.dropna()                    # 결측행 삭제
df.drop_duplicates()           # 중복 제거
df['col'].astype(float)        # 타입 변환
pd.get_dummies(df, columns=['category'])  # 원핫 인코딩
```

#### 5) 그룹 연산
```python
df.groupby('category')['score'].mean()   # 그룹별 평균
df.groupby('category').agg({'score': ['mean', 'std']})
df.pivot_table(values='score', index='age', columns='category')
```

#### 6) 병합
```python
pd.merge(df1, df2, on='id', how='inner')  # SQL JOIN
pd.concat([df1, df2], axis=0)             # 행 방향 합치기
```

---

## 3. Matplotlib

### 개념
- 파이썬 **기본 시각화 라이브러리**
- MATLAB 스타일 API 제공
- 거의 모든 차트 타입 지원 (저수준 제어 가능)
- seaborn, pandas 등이 내부적으로 matplotlib 사용

### 구조 이해
```
Figure (캔버스 전체)
  └── Axes (실제 그래프 영역, 여러 개 가능)
        ├── x축, y축
        ├── 제목
        └── 플롯 요소들
```

### 주요 차트 타입

| 차트 | 함수 | 사용 목적 |
|------|------|-----------|
| 선 그래프 | `plt.plot()` | 시계열, 학습 곡선 |
| 산점도 | `plt.scatter()` | 피처 관계, 클러스터 |
| 막대 그래프 | `plt.bar()` | 범주별 비교 |
| 히스토그램 | `plt.hist()` | 분포 확인 |
| 박스 플롯 | `plt.boxplot()` | 분포 + 이상치 |
| 히트맵 | `plt.imshow()` | 상관행렬, 혼동행렬 |

### 머신러닝 시각화 패턴
```python
# 학습 곡선 (train vs validation loss)
plt.plot(train_loss, label='Train')
plt.plot(val_loss, label='Validation')
plt.legend()
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Learning Curve')

# 결정 경계 시각화
plt.contourf(xx, yy, Z, alpha=0.4)
plt.scatter(X[:, 0], X[:, 1], c=y)
```

---

## 4. Seaborn

### 개념
- matplotlib 기반 **고수준 통계 시각화 라이브러리**
- 더 적은 코드로 더 예쁜 차트
- pandas DataFrame과 완벽 통합
- 통계적 시각화에 특화 (분포, 관계, 회귀 등)

### matplotlib vs seaborn 비교

| 항목 | matplotlib | seaborn |
|------|-----------|---------|
| 난이도 | 저수준, 세밀한 제어 | 고수준, 간결한 코드 |
| 기본 스타일 | 단순 | 세련됨 |
| 통계 지원 | 없음 | 내장 (회귀선, 신뢰구간 등) |
| DataFrame 연동 | 수동 변환 필요 | `data=df` 직접 지원 |

### 주요 함수

#### 분포 시각화
```python
sns.histplot(data=df, x='age', kde=True)   # 히스토그램 + KDE
sns.boxplot(data=df, x='category', y='score')
sns.violinplot(data=df, x='category', y='score')
```

#### 관계 시각화 (ML EDA 핵심)
```python
sns.scatterplot(data=df, x='x1', y='x2', hue='label')
sns.pairplot(df, hue='label')              # 모든 피처 쌍 관계
sns.heatmap(df.corr(), annot=True)         # 상관관계 히트맵
```

#### 회귀 시각화
```python
sns.regplot(data=df, x='x', y='y')        # 회귀선 자동 추가
sns.lmplot(data=df, x='x', y='y', hue='group')
```

### 머신러닝에서 활용
- EDA(탐색적 데이터 분석): `pairplot`, `heatmap`으로 피처 선택
- 모델 결과 시각화: 예측값 vs 실제값, 잔차 분포
- 클래스 불균형 확인: `countplot`

---

## 5. Scikit-learn ⭐ (이 강의 핵심)

### 개념
- 파이썬 **머신러닝 표준 라이브러리**
- 일관된 API: `fit()`, `predict()`, `transform()`
- 분류, 회귀, 군집화, 차원축소, 전처리 등 완비
- 학술 논문 수준 알고리즘 구현 제공

### 설계 철학: 일관된 API

모든 알고리즘이 **동일한 인터페이스** 를 따른다:

```
Estimator (추정기)
├── fit(X, y)         → 학습 (파라미터 추정)
├── predict(X)        → 예측 (지도학습)
├── transform(X)      → 변환 (전처리/차원축소)
├── fit_transform(X)  → 학습 + 변환 동시
└── score(X, y)       → 성능 평가
```

### 주요 모듈 구조

```
sklearn
├── datasets          → 연습용 데이터셋 (iris, digits, boston 등)
├── preprocessing     → 스케일링, 인코딩, 결측값 처리
├── model_selection   → 교차검증, 하이퍼파라미터 튜닝
├── linear_model      → 선형회귀, 로지스틱회귀, Ridge, Lasso
├── tree              → 결정트리
├── ensemble          → RandomForest, GradientBoosting
├── svm               → SVM (지지벡터머신)
├── neighbors         → KNN
├── cluster           → K-Means, DBSCAN
├── decomposition     → PCA, NMF
├── metrics           → 정확도, F1, RMSE 등 평가 지표
└── pipeline          → 전처리 + 모델 파이프라인
```

### 표준 ML 워크플로우

```python
# 1. 데이터 로드
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)

# 2. 데이터 분할
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. 전처리
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)  # 학습 데이터로 fit + transform
X_test  = scaler.transform(X_test)       # 테스트는 transform만!

# 4. 모델 생성 & 학습
from sklearn.svm import SVC
model = SVC(kernel='rbf', C=1.0)
model.fit(X_train, y_train)

# 5. 예측 & 평가
y_pred = model.predict(X_test)
from sklearn.metrics import accuracy_score, classification_report
print(accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
```

### 주요 알고리즘 (이후 챕터에서 상세 학습)

| 알고리즘 | 클래스 | 용도 |
|---------|--------|------|
| 선형회귀 | `LinearRegression` | 연속값 예측 |
| 로지스틱회귀 | `LogisticRegression` | 분류 |
| KNN | `KNeighborsClassifier` | 분류/회귀 |
| SVM | `SVC`, `SVR` | 분류/회귀 |
| 결정트리 | `DecisionTreeClassifier` | 분류/회귀 |
| 랜덤포레스트 | `RandomForestClassifier` | 분류/회귀 |
| K-Means | `KMeans` | 군집화 |
| PCA | `PCA` | 차원 축소 |

---

## 라이브러리 간 협력 관계

```
데이터 수집/로드
      │
   [pandas]  ← CSV, Excel, DB에서 로드, 전처리
      │
   [numpy]   ← 행렬/벡터 변환 (sklearn 입력 형식)
      │
[scikit-learn] ← 모델 학습, 예측, 평가
      │
[matplotlib / seaborn] ← 결과 시각화
```

---

## 설치 방법

```bash
pip install numpy pandas matplotlib seaborn scikit-learn
```

또는 한 번에:
```bash
pip install numpy pandas matplotlib seaborn scikit-learn jupyter
```

---

## 다음 단계

슬라이드 3장부터 각 라이브러리의 실제 코드 실습으로 진행합니다.
- `01_numpy_basics.ipynb`
- `02_pandas_basics.ipynb`
- `03_matplotlib_seaborn.ipynb`
- `04_sklearn_intro.ipynb`