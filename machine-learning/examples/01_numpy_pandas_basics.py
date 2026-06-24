"""Basic NumPy/Pandas examples for the ML math/background lecture."""

import numpy as np
import pandas as pd


def main() -> None:
    rng = np.random.default_rng(seed=42)

    dice = rng.integers(1, 7, size=20)
    scores = pd.DataFrame(
        {
            "x1": rng.normal(loc=70, scale=10, size=10),
            "x2": rng.normal(loc=30, scale=5, size=10),
        }
    )
    scores["target"] = 0.8 * scores["x1"] + 0.2 * scores["x2"]

    print("dice:", dice.tolist())
    print("\nsummary:")
    print(scores.describe())
    print("\ncorrelation:")
    print(scores.corr(numeric_only=True))


if __name__ == "__main__":
    main()

