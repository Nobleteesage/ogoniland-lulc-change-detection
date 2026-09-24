import ee
import json

ee.Initialize(project="ee-goriola-obafemi-ogoniland")

gaul2 = ee.FeatureCollection("FAO/GAUL/2015/level2")
OGONI_LGAS = ["Khana", "Gokana", "Tai", "Eleme"]

aoi = gaul2.filter(
    ee.Filter.And(
        ee.Filter.eq("ADM1_NAME", "Rivers"),
        ee.Filter.inList("ADM2_NAME", OGONI_LGAS),
    )
)

geojson = aoi.getInfo()

with open("data/ogoni_lgas.geojson", "w") as f:
    json.dump(geojson, f)

names = [feat["properties"]["ADM2_NAME"] for feat in geojson["features"]]
print(f"Saved {len(names)} LGA boundaries: {names}")
