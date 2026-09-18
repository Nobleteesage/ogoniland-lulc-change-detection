import rasterio
import numpy as np
import os

EPOCHS = ["1990", "2010", "2023"]
PIXEL_AREA_KM2 = (30 * 30) / 1_000_000  # 30m x 30m Landsat pixel, in km^2

CLASS_NAMES = {
    0: "Water",
    1: "Bare/Built-up/Degraded",
    2: "Moderate Vegetation",
    3: "Dense Vegetation/Mangrove",
}

os.makedirs("data/classified", exist_ok=True)

for epoch in EPOCHS:
    idx_path = f"data/processed/ogoniland_{epoch}_indices.tif"
    with rasterio.open(idx_path) as src:
        profile = src.profile
        ndvi = src.read(1)
        mndwi = src.read(3)

    valid = ~np.isnan(ndvi)

    classified = np.full(ndvi.shape, -1, dtype=np.int16)
    classified[valid & (mndwi > -0.1)] = 0
    classified[valid & (mndwi <= -0.1) & (ndvi < 0.40)] = 1
    classified[valid & (mndwi <= -0.1) & (ndvi >= 0.40) & (ndvi < 0.52)] = 2
    classified[valid & (mndwi <= -0.1) & (ndvi >= 0.52)] = 3

    out_profile = profile.copy()
    out_profile.update(count=1, dtype="int16", nodata=-1)
    out_path = f"data/classified/ogoniland_{epoch}_final.tif"
    with rasterio.open(out_path, "w", **out_profile) as dst:
        dst.write(classified, 1)

    print(f"\n=== {epoch} ===")
    total_valid = (classified >= 0).sum()
    for code, name in CLASS_NAMES.items():
        count = (classified == code).sum()
        area = count * PIXEL_AREA_KM2
        pct = 100 * count / total_valid
        print(f"  {name}: {count} px, {area:.2f} km^2, {pct:.1f}%")

    print(f"Saved: {out_path}")
