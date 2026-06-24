"""Time-series windowing starter for the Jena climate lecture."""

import numpy as np


def make_windows(series: np.ndarray, lookback: int, horizon: int) -> tuple[np.ndarray, np.ndarray]:
    x, y = [], []
    max_start = len(series) - lookback - horizon + 1
    for start in range(max_start):
        end = start + lookback
        x.append(series[start:end])
        y.append(series[end + horizon - 1])
    return np.array(x), np.array(y)


def main() -> None:
    series = np.sin(np.linspace(0, 20, 200))
    x, y = make_windows(series, lookback=24, horizon=3)
    print(f"x shape: {x.shape}")
    print(f"y shape: {y.shape}")
    print(f"first target: {y[0]:.3f}")


if __name__ == "__main__":
    main()

