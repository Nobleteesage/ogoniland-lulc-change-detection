import numpy as np
import rasterio
from rasterio.features import rasterize
import geopandas as gpd
import csv

PIXEL_AREA_KM2 = (30 * 30) / 1_000_000
CLASS_NAMES = {0: "Water", 1: "Bare/Degraded", 2: "ModerateVeg", 3: "DenseVeg/Mangrove"}
EPOCHS = ["1990", "2010", "2023"]

gdf = gpd.read_file("data/ogoni_lgas.geojson")
lga_names = gdf["ADM2_NAME"].tolist()
print(f"LGAs loaded: {lga_names}")

with rasterio.open("data/classified/ogoniland_1990_final.tif") as src:
    ref_transform = src.transform
    ref_shape = (src.height, src.width)

shapes = [(geom, i + 1) for i, geom in enumerate(gdf.geometry)]
zone_raster = rasterize(shapes, out_shape=ref_shape, transform=ref_transform, fill=0, dtype="int16")

for i, lga in enumerate(lga_names, start=1):
    px_count = np.sum(zone_raster == i)
    print(f"  {lga}: {px_count} pixels ({px_count * PIXEL_AREA_KM2:.1f} km^2 zone area)")

results = {}
for epoch in EPOCHS:
    with rasterio.open(f"data/classified/ogoniland_{epoch}_final.tif") as src:
        classified = src.read(1)

    for i, lga in enumerate(lga_names, start=1):
        zone_mask = (zone_raster == i) & (classified >= 0)
        for code, name in CLASS_NAMES.items():
            area = np.sum(zone_mask & (classified == code)) * PIXEL_AREA_KM2
            results[(lga, epoch, name)] = area

print(f"\n{'LGA':<10}{'Epoch':<8}{'Water':>10}{'Bare':>10}{'ModVeg':>10}{'DenseVeg':>10}")
for lga in lga_names:
    for epoch in EPOCHS:
        vals = [results[(lga, epoch, name)] for name in CLASS_NAMES.values()]
        print(f"{lga:<10}{epoch:<8}" + "".join(f"{v:10.2f}" for v in vals))

with open("data/classified/zonal_stats.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["LGA", "Epoch"] + list(CLASS_NAMES.values()))
    for lga in lga_names:
        for epoch in EPOCHS:
            vals = [results[(lga, epoch, name)] for name in CLASS_NAMES.values()]
            writer.writerow([lga, epoch] + [f"{v:.2f}" for v in vals])

print("\nSaved: data/classified/zonal_stats.csv")
