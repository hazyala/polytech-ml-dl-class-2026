import argparse
import json

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from config import (
    FIGURE_DIR,
    HORIZONS_SECONDS,
    MODEL_DIR,
    PROCESSED_DIR,
    RANDOM_STATE,
    REPORT_DIR,
    TEST_SIZE,
    lag_feature_columns,
)
from data_utils import build_prediction_dataset, dataset_summary, horizon_to_steps


def rmse(y_true, y_pred):
    return mean_squared_error(y_true, y_pred) ** 0.5


def train_one_horizon(horizon_seconds, save_processed=False, limit_files=None):
    df = build_prediction_dataset(horizon_seconds, limit_files=limit_files)

    feature_columns = lag_feature_columns()
    X = df[feature_columns]
    y = df["target_gas_leak"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_scaled, y_train)

    train_pred = model.predict(X_train_scaled)
    test_pred = model.predict(X_test_scaled)

    metrics = {
        "horizon_seconds": horizon_seconds,
        "horizon_steps": horizon_to_steps(horizon_seconds),
        "rows": len(df),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "train_mse": mean_squared_error(y_train, train_pred),
        "train_mae": mean_absolute_error(y_train, train_pred),
        "train_rmse": rmse(y_train, train_pred),
        "train_r2": r2_score(y_train, train_pred),
        "test_mse": mean_squared_error(y_test, test_pred),
        "test_mae": mean_absolute_error(y_test, test_pred),
        "test_rmse": rmse(y_test, test_pred),
        "test_r2": r2_score(y_test, test_pred),
    }

    model_bundle = {
        "horizon_seconds": horizon_seconds,
        "horizon_steps": horizon_to_steps(horizon_seconds),
        "feature_columns": feature_columns,
        "scaler": scaler,
        "model": model,
        "metrics": metrics,
    }

    joblib.dump(model_bundle, MODEL_DIR / f"gas_leak_linear_{horizon_seconds}s.joblib")

    if save_processed:
        df.to_csv(PROCESSED_DIR / f"gas_leak_{horizon_seconds}s_dataset.csv", index=False)

    plot_prediction_scatter(y_test, test_pred, horizon_seconds)
    return metrics


def plot_prediction_scatter(y_true, y_pred, horizon_seconds):
    plt.figure(figsize=(6, 6))
    plt.scatter(y_true, y_pred, s=5, alpha=0.25)

    min_value = min(y_true.min(), y_pred.min())
    max_value = max(y_true.max(), y_pred.max())
    plt.plot([min_value, max_value], [min_value, max_value], color="red")

    plt.title(f"Gas Leak Prediction: {horizon_seconds} seconds later")
    plt.xlabel("Actual Gas_Leak")
    plt.ylabel("Predicted Gas_Leak")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / f"prediction_scatter_{horizon_seconds}s.png", dpi=150)
    plt.close()


def save_outputs(metrics_df):
    summary_df = dataset_summary()
    summary_df.to_csv(REPORT_DIR / "dataset_summary.csv", index=False)

    metrics_df.to_csv(REPORT_DIR / "metrics.csv", index=False)

    with (REPORT_DIR / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics_df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save-processed", action="store_true")
    parser.add_argument("--limit-files", type=int, default=None)
    return parser.parse_args()


def main():
    args = parse_args()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    all_metrics = []
    for horizon_seconds in HORIZONS_SECONDS:
        print(f"Training {horizon_seconds}s model...")
        metrics = train_one_horizon(
            horizon_seconds,
            save_processed=args.save_processed,
            limit_files=args.limit_files,
        )
        all_metrics.append(metrics)
        print(metrics)

    metrics_df = pd.DataFrame(all_metrics)
    save_outputs(metrics_df)
    print("Done.")


if __name__ == "__main__":
    main()
