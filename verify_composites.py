import rasterio

files = [
    "data/raw/ogoniland_1990.tif",
    "data/raw/ogoniland_2010.tif",
    "data/raw/ogoniland_2023.tif",
]

for f in files:
    with rasterio.open(f) as src:
        print(f"\n{f}")
        print(f"  CRS: {src.crs}")
        print(f"  Shape: {src.width} x {src.height} pixels, {src.count} bands")
        print(f"  Bounds: {src.bounds}")
        data = src.read(1)
        print(f"  Band 1 (Red) min/max: {data.min()} / {data.max()}")
