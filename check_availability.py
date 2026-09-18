import ee

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

l5 = ee.ImageCollection("LANDSAT/LT05/C02/T1_L2").filterBounds(aoi_geom)

print("Landsat 5 images per year over Ogoniland (all months, no cloud filtering yet):")
for year in range(1999, 2013):
    start = f"{year}-01-01"
    end = f"{year}-12-31"
    count = l5.filterDate(start, end).size().getInfo()
    print(f"  {year}: {count} images")
