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

l7 = ee.ImageCollection("LANDSAT/LE07/C02/T1_L2").filterBounds(aoi_geom)

DRY_SEASON = ee.Filter.Or(
    ee.Filter.calendarRange(11, 12, "month"),
    ee.Filter.calendarRange(1, 3, "month"),
)

print("Landsat 7 images per year over Ogoniland:")
print(f"{'Year':<6}{'Full year':<12}{'Dry season only':<16}")
for year in range(1999, 2014):
    start = f"{year}-01-01"
    end = f"{year}-12-31"
    yearly = l7.filterDate(start, end)
    full_count = yearly.size().getInfo()
    dry_count = yearly.filter(DRY_SEASON).size().getInfo()
    print(f"{year:<6}{full_count:<12}{dry_count:<16}")
