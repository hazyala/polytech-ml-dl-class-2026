import re
from pathlib import Path

import pandas as pd

from config import DATASET_DIR, FEATURE_COLUMNS, LAG_STEPS, SENSOR_TO_FEATURE, SENSORS, lag_feature_columns


def horizon_to_steps(seconds):
    return int(seconds * 10)


def get_experiment_ids(dataset_dir=DATASET_DIR):
    first_sensor_dir = Path(dataset_dir) / SENSORS[0]
    ids = []

    for csv_path in first_sensor_dir.glob("*.csv"):
        match = re.search(r"_(\d{5})\.csv$", csv_path.name)
        if match:
            ids.append(int(match.group(1)))

    return sorted(ids)


def read_sensor_csv(sensor, experiment_id, dataset_dir=DATASET_DIR):
    csv_path = (
        Path(dataset_dir)
        / sensor
        / f"{sensor}_data_set_{experiment_id:05d}.csv"
    )
    df = pd.read_csv(csv_path, header=None, names=["time", SENSOR_TO_FEATURE[sensor]])
    return df


def load_experiment(experiment_id, dataset_dir=DATASET_DIR):
    merged = None

    for sensor in SENSORS:
        sensor_df = read_sensor_csv(sensor, experiment_id, dataset_dir)
        if merged is None:
            merged = sensor_df
        else:
            merged = pd.merge(merged, sensor_df, on="time", how="inner")

    merged["experiment_id"] = experiment_id
    return merged


def add_lag_features(df):
    result = df[["experiment_id", "time"]].copy()

    for lag_step in LAG_STEPS:
        suffix = "now" if lag_step == 0 else f"lag_{lag_step}"
        for column in FEATURE_COLUMNS:
            result[f"{column}_{suffix}"] = df[column].shift(lag_step)

    return result


def build_prediction_dataset(horizon_seconds, dataset_dir=DATASET_DIR, limit_files=None):
    horizon_steps = horizon_to_steps(horizon_seconds)
    frames = []
    experiment_ids = get_experiment_ids(dataset_dir)

    if limit_files is not None:
        experiment_ids = experiment_ids[:limit_files]

    for experiment_id in experiment_ids:
        df = load_experiment(experiment_id, dataset_dir)
        feature_df = add_lag_features(df)
        feature_df["target_gas_leak"] = df["gas_leak"].shift(-horizon_steps)
        feature_df = feature_df.dropna()
        frames.append(feature_df[["experiment_id", "time"] + lag_feature_columns() + ["target_gas_leak"]])

    return pd.concat(frames, ignore_index=True)


def dataset_summary(dataset_dir=DATASET_DIR):
    rows = []
    for sensor in SENSORS:
        sensor_dir = Path(dataset_dir) / sensor
        csv_files = sorted(sensor_dir.glob("*.csv"))
        first_df = pd.read_csv(csv_files[0], header=None, names=["time", "value"])

        rows.append(
            {
                "sensor": sensor,
                "csv_count": len(csv_files),
                "rows_per_csv": len(first_df),
                "time_start": first_df["time"].iloc[0],
                "time_end": first_df["time"].iloc[-1],
                "value_min_first_file": first_df["value"].min(),
                "value_max_first_file": first_df["value"].max(),
            }
        )

    return pd.DataFrame(rows)
