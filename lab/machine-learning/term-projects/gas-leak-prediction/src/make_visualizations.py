import joblib
import matplotlib.pyplot as plt
import pandas as pd

from config import FEATURE_COLUMNS, FIGURE_DIR, HORIZONS_SECONDS, MODEL_DIR, REPORT_DIR
from data_utils import build_prediction_dataset, load_experiment


def plot_sensor_example(experiment_id=0):
    df = load_experiment(experiment_id)

    fig, axes = plt.subplots(3, 2, figsize=(12, 9), sharex=True)
    axes = axes.ravel()

    for ax, column in zip(axes, FEATURE_COLUMNS):
        ax.plot(df["time"], df[column], linewidth=1)
        ax.set_title(column)
        ax.set_ylabel("value")

    axes[-1].set_xlabel("timestamp (100 ms)")
    axes[-2].set_xlabel("timestamp (100 ms)")
    fig.suptitle(f"Sensor Time Series Example: data_set_{experiment_id:05d}")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "sensor_time_series_example.png", dpi=150)
    plt.close(fig)


def plot_metric_bars():
    metrics_df = pd.read_csv(REPORT_DIR / "metrics.csv")

    plt.figure(figsize=(8, 5))
    plt.bar(metrics_df["horizon_seconds"].astype(str), metrics_df["test_rmse"])
    plt.title("RMSE by Prediction Horizon")
    plt.xlabel("prediction horizon (seconds)")
    plt.ylabel("test RMSE")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "rmse_by_horizon.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.bar(metrics_df["horizon_seconds"].astype(str), metrics_df["test_r2"])
    plt.title("R2 by Prediction Horizon")
    plt.xlabel("prediction horizon (seconds)")
    plt.ylabel("test R2")
    plt.ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "r2_by_horizon.png", dpi=150)
    plt.close()


def plot_actual_vs_predicted_lines(sample_rows=300):
    for horizon_seconds in HORIZONS_SECONDS:
        bundle = joblib.load(MODEL_DIR / f"gas_leak_linear_{horizon_seconds}s.joblib")
        df = build_prediction_dataset(horizon_seconds, limit_files=1)
        df = df.sort_values(["experiment_id", "time"]).head(sample_rows)

        X = df[bundle["feature_columns"]]
        X_scaled = bundle["scaler"].transform(X)
        y_pred = bundle["model"].predict(X_scaled)

        plt.figure(figsize=(11, 5))
        plt.plot(df["time"], df["target_gas_leak"], label="actual", linewidth=1.5)
        plt.plot(df["time"], y_pred, label="predicted", linewidth=1.5, alpha=0.85)
        plt.title(f"Actual vs Predicted Gas_Leak: {horizon_seconds} seconds later")
        plt.xlabel("timestamp (100 ms)")
        plt.ylabel("Gas_Leak")
        plt.legend()
        plt.tight_layout()
        plt.savefig(FIGURE_DIR / f"actual_vs_predicted_line_{horizon_seconds}s.png", dpi=150)
        plt.close()


def main():
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plot_sensor_example()
    plot_metric_bars()
    plot_actual_vs_predicted_lines()
    print("Visualizations saved.")


if __name__ == "__main__":
    main()
