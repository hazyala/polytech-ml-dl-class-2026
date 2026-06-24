import os
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
LAB_DIR = PROJECT_DIR.parents[2]
DATASET_DIR = Path(os.environ.get("GAS_LEAK_DATASET_DIR", LAB_DIR / "datasets" / "gas-leak-sample"))

DATA_DIR = PROJECT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = PROJECT_DIR / "models"
REPORT_DIR = PROJECT_DIR / "report"
FIGURE_DIR = REPORT_DIR / "figures"

SENSORS = [
    "Accelerometer",
    "Gas_Leak",
    "Pressure_1",
    "Pressure_2",
    "Temperature_1",
    "Temperature_2",
]

FEATURE_COLUMNS = [
    "accelerometer",
    "gas_leak",
    "pressure_1",
    "pressure_2",
    "temperature_1",
    "temperature_2",
]

SENSOR_TO_FEATURE = dict(zip(SENSORS, FEATURE_COLUMNS))

HORIZONS_SECONDS = [3, 9, 30, 60, 120]
STEP_SECONDS = 0.1
LAG_STEPS = [0, 10, 30, 60]
RANDOM_STATE = 42
TEST_SIZE = 0.2


def lag_feature_columns():
    columns = []
    for lag_step in LAG_STEPS:
        suffix = "now" if lag_step == 0 else f"lag_{lag_step}"
        for column in FEATURE_COLUMNS:
            columns.append(f"{column}_{suffix}")
    return columns
