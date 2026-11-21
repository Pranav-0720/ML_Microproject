"""Explore synthetic applicant profiles in standardized feature space."""
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from src.preprocessing import FEATURES, preprocessing


def analyze(profiles):
    inputs = preprocessing(normalize=True).fit_transform(profiles[FEATURES])
    candidates = [KMeans(n_clusters=k, random_state=42, n_init=10).fit(inputs)
                  for k in range(2, 6)]
    best = max(candidates, key=lambda model: silhouette_score(
        inputs, model.labels_, sample_size=800, random_state=42))
    pca = PCA(n_components=2)
    points = pca.fit_transform(inputs)
    result = profiles.copy()
    result["cluster"] = best.labels_.astype(str)
    result["PC1"], result["PC2"] = points.T
    return result, {
        "clusters": best.n_clusters,
        "variance_explained": pca.explained_variance_ratio_.tolist(),
        "silhouette": float(silhouette_score(inputs, best.labels_, sample_size=800, random_state=42)),
    }