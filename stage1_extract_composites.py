"""
Stage 1 - Ogoniland LULC change project (v3)
1990: Landsat 5 (1987-1993 window)
2010: Landsat 7 (2009-2012 window, aligned with UNEP assessment period)
2023: Landsat 8 (2022-2024 window)
"""

import os
import ee
import geemap

ee.Initialize(project="ee-goriola-obafemi-ogoniland")

gaul2 = ee.FeatureCollection("FAO/GAUL/2015/level2")
OGONI_LGAS = ["Khana", "Gokana", "Tai", "Eleme"]

aoi = gaul2.filter(
    ee.Filter.And(
        ee.Filter.eq("ADM1_NAME", "Rivers"),
        ee.Filter.inList("ADM2_NAME", OGONI_LGAS),
    )
)
aoi_geom = aoi.geometry()

SR_SCALE = 0.0000275
SR_OFFSET = -0.2

DRY_SEASON = ee.Filter.Or(
    ee.Filter.calendarRange(11, 12, "month"),
    ee.Filter.calendarRange(1, 3, "month"),
)


def _scale(image):
    optical = image.select("SR_B.*").multiply(SR_SCALE).add(SR_OFFSET)
    return image.addBands(optical, None, True)


def mask_tm_etm(image):
    """Works for Landsat 4/5 TM and Landsat 7 ETM+ (same band layout)."""
    qa = image.select("QA_PIXEL")
    cloud_shadow = 1 << 4
    cloud = 1 << 3
    mask = qa.bitwiseAnd(cloud_shadow).eq(0).And(qa.bitwiseAnd(cloud).eq(0))
    return _scale(image).updateMask(mask)


def mask_oli(image):
    """Landsat 8/9 OLI."""
    qa = image.select("QA_PIXEL")
    cloud_shadow = 1 << 4
    cloud = 1 << 3
    cirrus = 1 << 2
    mask = (
        qa.bitwiseAnd(cloud_shadow)
        .eq(0)
        .And(qa.bitwiseAnd(cloud).eq(0))
        .And(qa.bitwiseAnd(cirrus).eq(0))
    )
    return _scale(image).updateMask(mask)


def get_composite(label, collection_id, start, end, mask_fn, bands, band_names):
    coll = (
        ee.ImageCollection(collection_id)
        .filterBounds(aoi_geom)
        .filterDate(start, end)
        .filter(DRY_SEASON)
        .map(mask_fn)
    )
    count = coll.size().getInfo()
    print(f"  {label}: {count} images matched before compositing")
    if count == 0:
        raise RuntimeError(f"No images found for {label} - widen the date range")

    composite = coll.median().select(bands, band_names).clip(aoi_geom)
    composite = composite.multiply(10000).toInt16()
    return composite


TM_ETM_BANDS = ["SR_B3", "SR_B2", "SR_B1", "SR_B4", "SR_B5", "SR_B7"]
OLI_BANDS = ["SR_B4", "SR_B3", "SR_B2", "SR_B5", "SR_B6", "SR_B7"]

EPOCHS = {
    "1990": dict(
        collection="LANDSAT/LT05/C02/T1_L2",
        start="1984-01-01", end="1996-12-31",
        mask_fn=mask_tm_etm, bands=TM_ETM_BANDS,
    ),
    "2010": dict(
        collection="LANDSAT/LE07/C02/T1_L2",
        start="2009-01-01", end="2012-12-31",
        mask_fn=mask_tm_etm, bands=TM_ETM_BANDS,
    ),
    "2023": dict(
        collection="LANDSAT/LC08/C02/T1_L2",
        start="2022-01-01", end="2024-12-31",
        mask_fn=mask_oli, bands=OLI_BANDS,
    ),
}

BAND_NAMES = ["Red", "Green", "Blue", "NIR", "SWIR1", "SWIR2"]

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)

    for label, cfg in EPOCHS.items():
        out_path = f"data/raw/ogoniland_{label}.tif"

        if os.path.exists(out_path):
            size_mb = os.path.getsize(out_path) / (1024 * 1024)
            print(f"Skipping {label} - already exists ({size_mb:.1f} MB)")
            continue

        print(f"Building composite for {label}...")
        try:
            image = get_composite(
                label, cfg["collection"], cfg["start"], cfg["end"],
                cfg["mask_fn"], cfg["bands"], BAND_NAMES,
            )
            geemap.ee_export_image(
                image, filename=out_path, scale=30,
                region=aoi_geom, file_per_band=False,
            )
            if os.path.exists(out_path):
                size_mb = os.path.getsize(out_path) / (1024 * 1024)
                print(f"  -> confirmed exported {out_path} ({size_mb:.1f} MB)")
            else:
                print(f"  -> FAILED, no file written for {label}")
        except Exception as e:
            print(f"  -> FAILED for {label}: {e}")

    print("Done.")
