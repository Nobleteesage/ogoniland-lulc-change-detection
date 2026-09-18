# Ogoniland Land-Use/Land-Cover Change Detection (1990–2023)

Multi-decadal remote sensing analysis of land-cover change in Ogoniland
(Khana, Gokana, Tai, and Eleme LGAs, Rivers State, Nigeria), examining
the environmental trajectory before and after the 2011 UNEP
Environmental Assessment of Ogoniland.

## Data

- **Source:** Landsat Collection 2 Level-2 surface reflectance, via Google Earth Engine
- **Sensors:** Landsat 5 TM (1990 epoch), Landsat 7 ETM+ (2010 epoch), Landsat 8 OLI (2023 epoch)
- **Compositing:** Cloud-masked dry-season (Nov–Mar) median composites
- **Study area boundary:** FAO GAUL 2015 administrative boundaries (Rivers State, Nigeria)

| Epoch | Date range | Images composited |
|---|---|---|
| 1990 | 1984–1996 | 8 |
| 2010 | 2009–2012 | 20 |
| 2023 | 2022–2024 | 24 |

## Method

1. Cloud/shadow masking via QA_PIXEL bit flags
2. Computed NDVI, NDWI, and MNDWI per epoch
3. Classified into four categories using fixed index thresholds
   (validated against K-Means cluster analysis of each epoch):
   - Water: MNDWI > -0.1
   - Bare/Built-up/Degraded: NDVI < 0.40
   - Moderate Vegetation: 0.40 ≤ NDVI < 0.52
   - Dense Vegetation/Mangrove: NDVI ≥ 0.52
4. Pixel-level post-classification change detection between epochs

## Key findings

- Bare/Degraded land rose from 114.7 km² (1990) to a peak of 171.0 km²
  (2010, coinciding with the UNEP assessment period), then fell to 80.5 km²
  by 2023 — below the 1990 baseline.
- Dense Vegetation/Mangrove more than doubled, from 173.3 km² (1990) to
  398.7 km² (2023), a 130% increase.
- Net transitions confirm the pattern at the pixel level: 1990–2010 shows
  a net +56.0 km² conversion of vegetation to degraded land; 2010–2023
  shows a net -92.5 km² reversal.

## Limitations

- Landsat 5 has a well-documented historical coverage gap over West Africa;
  the "2010" epoch uses Landsat 7 instead, composited over 2009-2012 to
  compensate for post-2003 scan-line-corrector gaps.
- Fixed-threshold classification shows substantial bidirectional churn
  between the two vegetation classes in every period, a known artifact
  of hard thresholds near class boundaries; net-direction consistency
  across independently-computed periods supports the overall trend.
- No ground-truth field validation was available for the 1990 or 2010
  epochs; classification thresholds were derived from empirical cluster
  analysis rather than labeled training data.

## Reproducing this analysis

```bash
python3 stage1_extract_composites.py    # pulls Landsat composites via GEE
python3 compute_indices.py              # NDVI/NDWI/MNDWI per epoch
python3 classify_final.py               # threshold-based classification
python3 change_matrix.py                # pixel transition matrices
python3 visualize_classification.py     # comparison map
```

Requires: `earthengine-api`, `geemap`, `rasterio`, `numpy`, `scikit-learn`,
`matplotlib`. Requires a registered Google Earth Engine project
(free, Community Tier — see https://code.earthengine.google.com/register).
