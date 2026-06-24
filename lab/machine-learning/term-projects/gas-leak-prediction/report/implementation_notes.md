# 가스환경 예측 모델 구현 작업 기록

## 작업 목표

- `/workspace/dataset`에 있는 6개 센서 CSV 데이터를 사용하여 `Gas_Leak` 미래 값을 예측한다.
- 예측 시점은 3초 후, 9초 후, 30초 후, 60초 후, 120초 후이다.
- 각 예측 시점마다 별도 모델을 학습하여 총 5개 모델 파일을 저장한다.
- 강의자료의 회귀 분석 흐름에 맞춰 `pandas`, `train_test_split`, `StandardScaler`, `LinearRegression`, `fit`, `predict`, `MSE/MAE/RMSE/R2` 중심으로 구현한다.
- 시계열 분석 내용을 반영하기 위해 현재 시점뿐 아니라 과거 시점의 센서값을 lag feature로 함께 사용한다.
- PNG 파일은 CSV 시계열을 시각화한 참고 자료이므로 학습에는 사용하지 않는다.

## 현재 데이터 구조 확인

- 데이터 위치: `/workspace/dataset`
- 센서 폴더 6개:
  - `Accelerometer`
  - `Gas_Leak`
  - `Pressure_1`
  - `Pressure_2`
  - `Temperature_1`
  - `Temperature_2`
- 각 센서 폴더에는 CSV 1000개와 PNG 1000개가 있다.
- CSV 번호는 `00000`부터 `00999`까지 연속되어 있어 같은 번호끼리 병합할 수 있다.
- 각 CSV는 3000행 2열이다.
  - 1열: timestamp
  - 2열: sensor value
- PNG 그래프의 x축 라벨이 `Timestamp(100 Millisecond)`이므로 1 step은 0.1초로 처리하였다.

## 예측 시점 변환

`ml_term_gas/src/data_utils.py`의 `horizon_to_steps()`에서 초 단위를 step 단위로 변환한다.

```python
def horizon_to_steps(seconds):
    return int(seconds * 10)
```

따라서 예측 시점은 다음처럼 변환된다.

| 예측 시점 | step |
|---:|---:|
| 3초 | 30 |
| 9초 | 90 |
| 30초 | 300 |
| 60초 | 600 |
| 120초 | 1200 |

## 생성한 코드 파일

### `ml_term_gas/src/config.py`

프로젝트에서 반복해서 쓰는 경로, 센서명, 특징명, 예측 시점, 학습 설정값을 모아 둔 파일이다.

핵심 설정:

```python
PROJECT_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = PROJECT_DIR.parent
DATASET_DIR = WORKSPACE_DIR / "dataset"
```

컨테이너에서 실행하면 `PROJECT_DIR`은 `/workspace/ml_term_gas`, `DATASET_DIR`은 `/workspace/dataset`이 된다.

기본 센서 컬럼은 6개이다.

```python
FEATURE_COLUMNS = [
    "accelerometer",
    "gas_leak",
    "pressure_1",
    "pressure_2",
    "temperature_1",
    "temperature_2",
]
```

예측 시점은 아래와 같이 고정하였다.

```python
HORIZONS_SECONDS = [3, 9, 30, 60, 120]
```

시계열 분석 내용을 반영하기 위해 현재 시점과 과거 1초, 3초, 6초의 값을 함께 사용한다.

```python
LAG_STEPS = [0, 10, 30, 60]
```

`lag_feature_columns()`는 6개 센서 컬럼에 lag step을 붙여 총 24개 입력 특징을 만든다.

예:

- `gas_leak_now`
- `gas_leak_lag_10`
- `gas_leak_lag_30`
- `gas_leak_lag_60`

### `ml_term_gas/src/data_utils.py`

CSV 읽기, 같은 번호의 6개 센서 병합, lag feature 생성, 미래 `Gas_Leak` 타깃 생성 기능을 담당한다.

`read_sensor_csv()`는 헤더가 없는 CSV를 읽어 `time`과 센서값 컬럼으로 이름을 붙인다.

```python
df = pd.read_csv(csv_path, header=None, names=["time", SENSOR_TO_FEATURE[sensor]])
```

`load_experiment()`는 같은 실험 번호의 6개 센서 CSV를 `time` 기준으로 병합한다.

```python
merged = pd.merge(merged, sensor_df, on="time", how="inner")
```

`add_lag_features()`는 현재 시점과 과거 시점의 센서값을 입력 특징으로 확장한다.

```python
for lag_step in LAG_STEPS:
    suffix = "now" if lag_step == 0 else f"lag_{lag_step}"
    for column in FEATURE_COLUMNS:
        result[f"{column}_{suffix}"] = df[column].shift(lag_step)
```

`build_prediction_dataset()`은 lag feature를 입력 `X`, 미래 시점의 `Gas_Leak` 값을 정답 `y`로 만들기 위해 `shift()`를 사용한다.

```python
feature_df = add_lag_features(df)
feature_df["target_gas_leak"] = df["gas_leak"].shift(-horizon_steps)
feature_df = feature_df.dropna()
```

이 방식은 예를 들어 3초 모델에서는 현재 및 과거 1초, 3초, 6초의 6개 센서값, 즉 총 24개 lag feature로 30 step 뒤의 `Gas_Leak` 값을 예측하게 한다.

## 시계열 분석 반영 보완

초기 구현은 현재 시점의 6개 센서값만 사용하여 미래 `Gas_Leak` 값을 예측하는 회귀 모델이었다. 이 방식도 미래 값을 `shift()`로 만드는 예측 문제이지만, 시계열 분석 관점에서는 과거 흐름 정보가 충분히 들어가지 않는다.

이를 보완하기 위해 최종 구현에서는 현재 시점뿐 아니라 과거 1초, 3초, 6초의 센서값을 함께 입력으로 사용하였다.

```text
입력 X =
  t 시점의 6개 센서값
  t-1초 시점의 6개 센서값
  t-3초 시점의 6개 센서값
  t-6초 시점의 6개 센서값

출력 y =
  t+n초 시점의 Gas_Leak 값
```

이 구조는 딥러닝 RNN/LSTM까지 사용하지 않더라도, 시계열 자료에서 과거 관측값을 이용해 미래 값을 예측한다는 시계열 분석의 핵심 아이디어를 회귀 모델 수준에서 반영한 것이다. 따라서 강의자료의 회귀 분석 코드 수준을 유지하면서도 시계열 분석 내용을 응용한 형태이다.

### `ml_term_gas/src/train_models.py`

5개 예측 모델을 학습하고 저장하는 메인 스크립트이다.

`train_one_horizon()`은 하나의 예측 시점에 대해 다음 순서로 실행된다.

1. `build_prediction_dataset()`으로 학습 데이터 생성
2. lag feature 24개를 입력 `X`, 미래 `Gas_Leak`를 정답 `y`로 분리
3. `train_test_split()`으로 훈련 80%, 검증 20% 분리
4. `StandardScaler()`로 입력 특징 표준화
5. `LinearRegression()` 모델 학습
6. `predict()`로 훈련/검증 데이터 예측
7. MSE, MAE, RMSE, R2 계산
8. `joblib.dump()`로 모델 저장
9. 예측값과 실제값 비교 scatter plot 저장

핵심 학습 코드:

```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = LinearRegression()
model.fit(X_train_scaled, y_train)
```

모델 저장 코드는 다음과 같다.

```python
model_bundle = {
    "horizon_seconds": horizon_seconds,
    "horizon_steps": horizon_to_steps(horizon_seconds),
    "feature_columns": feature_columns,
    "scaler": scaler,
    "model": model,
    "metrics": metrics,
}

joblib.dump(model_bundle, MODEL_DIR / f"gas_leak_linear_{horizon_seconds}s.joblib")
```

모델 파일은 `/workspace/ml_term_gas/models`에 아래 이름으로 저장되도록 구현하였다.

- `gas_leak_linear_3s.joblib`
- `gas_leak_linear_9s.joblib`
- `gas_leak_linear_30s.joblib`
- `gas_leak_linear_60s.joblib`
- `gas_leak_linear_120s.joblib`

### `ml_term_gas/src/make_visualizations.py`

학습된 모델과 성능 평가 결과를 바탕으로 보고서에 사용할 시각화 자료를 생성하는 스크립트이다.

실행 명령:

```bash
cd /workspace/ml_term_gas/src
python make_visualizations.py
```

`plot_sensor_example()`은 `data_set_00000`의 6개 센서 원본 시계열을 하나의 그림에 3행 2열 subplot으로 표시한다.

```python
df = load_experiment(experiment_id)

for ax, column in zip(axes, FEATURE_COLUMNS):
    ax.plot(df["time"], df[column], linewidth=1)
```

생성 파일:

- `/workspace/ml_term_gas/report/figures/sensor_time_series_example.png`

`plot_metric_bars()`는 `metrics.csv`를 읽어 예측 시간별 RMSE와 R2를 막대그래프로 비교한다.

```python
metrics_df = pd.read_csv(REPORT_DIR / "metrics.csv")
plt.bar(metrics_df["horizon_seconds"].astype(str), metrics_df["test_rmse"])
plt.bar(metrics_df["horizon_seconds"].astype(str), metrics_df["test_r2"])
```

생성 파일:

- `/workspace/ml_term_gas/report/figures/rmse_by_horizon.png`
- `/workspace/ml_term_gas/report/figures/r2_by_horizon.png`

`plot_actual_vs_predicted_lines()`는 저장된 5개 모델을 `joblib.load()`로 불러온 뒤, 첫 번째 실험 파일의 일부 구간에서 실제 `Gas_Leak` 값과 예측값을 선 그래프로 비교한다.

```python
bundle = joblib.load(MODEL_DIR / f"gas_leak_linear_{horizon_seconds}s.joblib")
X_scaled = bundle["scaler"].transform(X)
y_pred = bundle["model"].predict(X_scaled)
```

생성 파일:

- `/workspace/ml_term_gas/report/figures/actual_vs_predicted_line_3s.png`
- `/workspace/ml_term_gas/report/figures/actual_vs_predicted_line_9s.png`
- `/workspace/ml_term_gas/report/figures/actual_vs_predicted_line_30s.png`
- `/workspace/ml_term_gas/report/figures/actual_vs_predicted_line_60s.png`
- `/workspace/ml_term_gas/report/figures/actual_vs_predicted_line_120s.png`

## 결과 파일 계획

학습 완료 후 다음 파일들이 생성된다.

- `/workspace/ml_term_gas/models/gas_leak_linear_3s.joblib`
- `/workspace/ml_term_gas/models/gas_leak_linear_9s.joblib`
- `/workspace/ml_term_gas/models/gas_leak_linear_30s.joblib`
- `/workspace/ml_term_gas/models/gas_leak_linear_60s.joblib`
- `/workspace/ml_term_gas/models/gas_leak_linear_120s.joblib`
- `/workspace/ml_term_gas/report/metrics.csv`
- `/workspace/ml_term_gas/report/metrics.json`
- `/workspace/ml_term_gas/report/dataset_summary.csv`
- `/workspace/ml_term_gas/report/figures/prediction_scatter_3s.png`
- `/workspace/ml_term_gas/report/figures/prediction_scatter_9s.png`
- `/workspace/ml_term_gas/report/figures/prediction_scatter_30s.png`
- `/workspace/ml_term_gas/report/figures/prediction_scatter_60s.png`
- `/workspace/ml_term_gas/report/figures/prediction_scatter_120s.png`
- `/workspace/ml_term_gas/report/figures/sensor_time_series_example.png`
- `/workspace/ml_term_gas/report/figures/rmse_by_horizon.png`
- `/workspace/ml_term_gas/report/figures/r2_by_horizon.png`
- `/workspace/ml_term_gas/report/figures/actual_vs_predicted_line_3s.png`
- `/workspace/ml_term_gas/report/figures/actual_vs_predicted_line_9s.png`
- `/workspace/ml_term_gas/report/figures/actual_vs_predicted_line_30s.png`
- `/workspace/ml_term_gas/report/figures/actual_vs_predicted_line_60s.png`
- `/workspace/ml_term_gas/report/figures/actual_vs_predicted_line_120s.png`

## 실행 방법

컨테이너 `/workspace` 기준으로 아래 명령을 실행한다.

```bash
cd /workspace/ml_term_gas/src
python train_models.py
```

전처리된 전체 학습 데이터 CSV까지 저장하고 싶으면 아래처럼 실행한다.

```bash
cd /workspace/ml_term_gas/src
python train_models.py --save-processed
```

## 실행 검증 기록

### 샘플 실행

전체 학습 전에 컨테이너 `/workspace` 환경에서 5개 실험 파일만 사용해 스크립트 동작을 확인하였다.

```bash
cd /workspace/ml_term_gas/src
python train_models.py --limit-files 5
```

확인된 내용:

- 3초, 9초, 30초, 60초, 120초 모델 학습 루프가 모두 정상 실행되었다.
- `StandardScaler`, `LinearRegression`, `joblib.dump`, 성능 평가, scatter plot 저장이 정상 동작하였다.
- 샘플 실행 결과 생성된 모델 파일은 전체 학습 실행 시 같은 파일명으로 다시 덮어쓴다.

### 전체 데이터 학습 실행

컨테이너 `/workspace` 환경에서 전체 1000개 실험 파일을 사용해 최종 학습을 실행하였다.

```bash
cd /workspace/ml_term_gas/src
python train_models.py
```

최종 저장된 모델 파일:

| 파일 | 예측 시점 |
|---|---:|
| `/workspace/ml_term_gas/models/gas_leak_linear_3s.joblib` | 3초 후 |
| `/workspace/ml_term_gas/models/gas_leak_linear_9s.joblib` | 9초 후 |
| `/workspace/ml_term_gas/models/gas_leak_linear_30s.joblib` | 30초 후 |
| `/workspace/ml_term_gas/models/gas_leak_linear_60s.joblib` | 60초 후 |
| `/workspace/ml_term_gas/models/gas_leak_linear_120s.joblib` | 120초 후 |

최종 성능 요약:

| 예측 시점 | 데이터 행 수 | Test RMSE | Test MAE | Test R2 |
|---:|---:|---:|---:|---:|
| 3초 | 2,910,000 | 26.0540 | 18.2955 | 0.9938 |
| 9초 | 2,850,000 | 37.6477 | 26.9933 | 0.9868 |
| 30초 | 2,640,000 | 69.0520 | 50.0620 | 0.9531 |
| 60초 | 2,340,000 | 102.6994 | 75.6505 | 0.8880 |
| 120초 | 1,740,000 | 148.5925 | 111.5008 | 0.7209 |

전체 성능 수치는 `/workspace/ml_term_gas/report/metrics.csv`와 `/workspace/ml_term_gas/report/metrics.json`에 저장되어 있다.

### 저장 모델 로드 검증

학습 후 `joblib.load()`로 5개 모델 파일이 모두 정상 로드되는지 확인하였다.

확인된 내용:

- 각 모델 bundle에는 `horizon_seconds`, `horizon_steps`, `feature_columns`, `scaler`, `model`, `metrics`가 들어 있다.
- 5개 모델 모두 입력 특징이 동일하게 24개 lag feature로 저장되어 있다.
- 저장된 `test_r2` 값도 `metrics.csv`와 일치한다.

### 추가 시각화 실행

사용자 요청에 따라 보고서용 시각화 자료를 추가 생성하였다.

```bash
cd /workspace/ml_term_gas/src
python make_visualizations.py
```

추가 생성된 시각화:

| 파일 | 내용 |
|---|---|
| `sensor_time_series_example.png` | 6개 센서 원본 시계열 예시 |
| `rmse_by_horizon.png` | 예측 시간별 Test RMSE 비교 |
| `r2_by_horizon.png` | 예측 시간별 Test R2 비교 |
| `actual_vs_predicted_line_3s.png` | 3초 후 실제값과 예측값 일부 구간 비교 |
| `actual_vs_predicted_line_9s.png` | 9초 후 실제값과 예측값 일부 구간 비교 |
| `actual_vs_predicted_line_30s.png` | 30초 후 실제값과 예측값 일부 구간 비교 |
| `actual_vs_predicted_line_60s.png` | 60초 후 실제값과 예측값 일부 구간 비교 |
| `actual_vs_predicted_line_120s.png` | 120초 후 실제값과 예측값 일부 구간 비교 |
