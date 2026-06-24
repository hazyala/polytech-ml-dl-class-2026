"""Small KNN classifier implemented with NumPy only."""

from collections import Counter

import numpy as np


class SimpleKNN:
    def __init__(self, k: int = 3) -> None:
        self.k = k
        self.x_train: np.ndarray | None = None
        self.y_train: np.ndarray | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> None:
        self.x_train = x
        self.y_train = y

    def predict_one(self, x: np.ndarray) -> int:
        if self.x_train is None or self.y_train is None:
            raise RuntimeError("Call fit before predict.")
        distances = np.sqrt(np.sum((self.x_train - x) ** 2, axis=1))
        nearest = np.argsort(distances)[: self.k]
        vote = Counter(self.y_train[nearest])
        return int(vote.most_common(1)[0][0])

    def predict(self, x: np.ndarray) -> np.ndarray:
        return np.array([self.predict_one(row) for row in x])


def main() -> None:
    x = np.array(
        [
            [1.0, 1.0],
            [1.5, 1.2],
            [4.0, 4.0],
            [4.5, 3.8],
            [8.0, 1.0],
            [8.5, 1.3],
        ]
    )
    y = np.array([0, 0, 1, 1, 2, 2])
    test = np.array([[1.2, 1.1], [4.2, 3.9], [8.2, 1.2]])

    model = SimpleKNN(k=3)
    model.fit(x, y)
    print(model.predict(test).tolist())


if __name__ == "__main__":
    main()

