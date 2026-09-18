import rasterio
import numpy as np
import os

EPOCHS = ["1990", "2010", "2023"]
NODATA = -32768

os.makedirs("data/processed", exist_ok=True)

for epoch in EPOCHS:
    in_path = f"data/raw/ogoniland_{epoch}.tif"
    with rasterio.open(in_path) as src:
        profile = src.profile
        red = src.read(1).astype(np.float32)
        green = src.read(2).astype(np.float32)
        blue = src.read(3).astype(np.float32)
        nir = src.read(4).astype(np.float32)
        swir1 = src.read(5).astype(np.float32)
        swir2 = src.read(6).astype(np.float32)

    valid = (red != NODATA) & (nir != NODATA) & (green != NODATA) & (swir1 != NODATA)

    ndvi = np.where(valid, (nir - red) / (nir + red + 1e-6), np.nan)
    ndwi = np.where(valid, (green - nir) / (green + nir + 1e-6), np.nan)
    mndwi = np.where(valid, (green - swir1) / (green + swir1 + 1e-6), np.nan)

    # Clip to the indices' true mathematical range; anything outside is a
    # negative-reflectance artifact, not a real land-cover signal
    ndvi = np.clip(ndvi, -1, 1)
    ndwi = np.clip(ndwi, -1, 1)
    mndwi = np.clip(mndwi, -1, 1)

    print(f"\n{epoch}:")
    print(f"  NDVI   min/max/mean: {np.nanmin(ndvi):.3f} / {np.nanmax(ndvi):.3f} / {np.nanmean(ndvi):.3f}")
    print(f"  NDWI   min/max/mean: {np.nanmin(ndwi):.3f} / {np.nanmax(ndwi):.3f} / {np.nanmean(ndwi):.3f}")
    print(f"  MNDWI  min/max/mean: {np.nanmin(mndwi):.3f} / {np.nanmax(mndwi):.3f} / {np.nanmean(mndwi):.3f}")
    print(f"  Valid pixels: {valid.sum()} / {valid.size} ({100*valid.sum()/valid.size:.1f}%)")

    out_profile = profile.copy()
    out_profile.update(count=3, dtype="float32", nodata=np.nan)

    out_path = f"data/processed/ogoniland_{epoch}_indices.tif"
    with rasterio.open(out_path, "w", **out_profile) as dst:
        dst.write(ndvi, 1)
        dst.write(ndwi, 2)
        dst.write(mndwi, 3)
        dst.set_band_description(1, "NDVI")
        dst.set_band_description(2, "NDWI")
        dst.set_band_description(3, "MNDWI")

    print(f"  Saved: {out_path}")
