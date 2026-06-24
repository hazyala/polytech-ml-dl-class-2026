"""SVM starter example with linear, RBF, and polynomial kernels."""

from sklearn.datasets import make_moons
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def evaluate_kernel(kernel: str, **kwargs) -> float:
    x, y = make_moons(n_samples=300, noise=0.25, random_state=42)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = make_pipeline(StandardScaler(), SVC(kernel=kernel, **kwargs))
    model.fit(x_train, y_train)
    return accuracy_score(y_test, model.predict(x_test))


def main() -> None:
    scores = {
        "linear": evaluate_kernel("linear", C=1.0),
        "rbf": evaluate_kernel("rbf", C=3.0, gamma="scale"),
        "poly": evaluate_kernel("poly", C=3.0, degree=3, gamma="scale"),
    }
    for name, score in scores.items():
        print(f"{name:>6} kernel accuracy: {score:.3f}")


if __name__ == "__main__":
    main()

