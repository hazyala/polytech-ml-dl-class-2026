"""PCA starter example showing explained variance and dimensionality reduction."""

from sklearn.datasets import load_wine
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def main() -> None:
    data = load_wine()
    pca_pipeline = make_pipeline(StandardScaler(), PCA(n_components=2, random_state=42))
    projected = pca_pipeline.fit_transform(data.data)
    pca = pca_pipeline.named_steps["pca"]

    print(f"original shape: {data.data.shape}")
    print(f"projected shape: {projected.shape}")
    print("explained variance ratio:", [round(v, 3) for v in pca.explained_variance_ratio_])
    print("first projected row:", [round(v, 3) for v in projected[0]])


if __name__ == "__main__":
    main()

