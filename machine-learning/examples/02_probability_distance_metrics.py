"""Probability, vector, and distance examples for ML background math."""

import numpy as np


def euclidean(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.sum((a - b) ** 2)))


def manhattan(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sum(np.abs(a - b)))


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main() -> None:
    rng = np.random.default_rng(seed=7)
    samples = rng.normal(loc=0.0, scale=1.0, size=1000)

    a = np.array([1.0, 2.0, 3.0])
    b = np.array([2.0, 4.0, 4.0])

    print(f"mean: {samples.mean():.3f}")
    print(f"std: {samples.std():.3f}")
    print(f"P(x > 1): {(samples > 1).mean():.3f}")
    print(f"euclidean: {euclidean(a, b):.3f}")
    print(f"manhattan: {manhattan(a, b):.3f}")
    print(f"cosine similarity: {cosine_similarity(a, b):.3f}")


if __name__ == "__main__":
    main()

