"""Regression, SVM, and PCA examples for the ML lecture sequence."""

from sklearn.datasets import load_breast_cancer, load_diabetes
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def regression_demo() -> None:
    data = load_diabetes()
    x_train, x_test, y_train, y_test = train_test_split(
        data.data, data.target, random_state=42
    )
    model = LinearRegression()
    model.fit(x_train, y_train)
    print(f"Linear regression R2: {r2_score(y_test, model.predict(x_test)):.3f}")


def svm_pca_demo() -> None:
    data = load_breast_cancer()
    x_train, x_test, y_train, y_test = train_test_split(
        data.data,
        data.target,
        test_size=0.25,
        random_state=42,
        stratify=data.target,
    )

    svm = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=3.0, gamma="scale"))
    svm.fit(x_train, y_train)
    print(f"SVM accuracy: {accuracy_score(y_test, svm.predict(x_test)):.3f}")

    pca_model = make_pipeline(StandardScaler(), PCA(n_components=2, random_state=42))
    projected = pca_model.fit_transform(data.data)
    explained = pca_model.named_steps["pca"].explained_variance_ratio_
    print(f"PCA shape: {projected.shape}")
    print(f"PCA explained variance: {explained[0]:.3f}, {explained[1]:.3f}")


def main() -> None:
    regression_demo()
    svm_pca_demo()


if __name__ == "__main__":
    main()

