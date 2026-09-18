import rasterio
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

EPOCHS = ["1990", "2010", "2023"]
NODATA = -32768
N_CLUSTERS = 5
BAND_NAMES = ["Red", "Green", "Blue", "NIR", "SWIR1", "SWIR2", "NDVI", "NDWI", "MNDWI"]

os.makedirs("data/classified", exist_ok=True)

for epoch in EPOCHS:
    raw_path = f"data/raw/ogoniland_{epoch}.tif"
    idx_path = f"data/processed/ogoniland_{epoch}_indices.tif"

    with rasterio.open(raw_path) as src:
        profile = src.profile
        bands = src.read().astype(np.float32)  # (6, H, W)

    with rasterio.open(idx_path) as src:
        indices = src.read()  # (3, H, W): NDVI, NDWI, MNDWI

    valid = (bands[0] != NODATA) & ~np.isnan(indices[0])

    stacked = np.concatenate([bands, indices], axis=0)  # (9, H, W)
    n_features, height, width = stacked.shape

    flat = stacked.reshape(n_features, -1).T
    valid_flat = valid.reshape(-1)
    X = flat[valid_flat]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)

    full_labels = np.full(flat.shape[0], -1, dtype=np.int16)
    full_labels[valid_flat] = cluster_labels
    label_raster = full_labels.reshape(height, width)

    out_profile = profile.copy()
    out_profile.update(count=1, dtype="int16", nodata=-1)
    out_path = f"data/classified/ogoniland_{epoch}_clusters.tif"
    with rasterio.open(out_path, "w", **out_profile) as dst:
        dst.write(label_raster, 1)

    print(f"\n=== {epoch} ===")
    print(f"Cluster sizes: {np.bincount(cluster_labels)}")
    for c in range(N_CLUSTERS):
        mask = cluster_labels == c
        means = X[mask].mean(axis=0)
        pct = 100 * mask.sum() / len(cluster_labels)
        print(f"\n  Cluster {c} (n={mask.sum()}, {pct:.1f}% of image):")
        for name, val in zip(BAND_NAMES, means):
            print(f"    {name}: {val:.3f}")

    print(f"\nSaved: {out_path}")
