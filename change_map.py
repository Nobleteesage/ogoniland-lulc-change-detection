import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

with rasterio.open("data/classified/ogoniland_1990_final.tif") as src:
    c1990 = src.read(1)
    profile = src.profile

with rasterio.open("data/classified/ogoniland_2023_final.tif") as src:
    c2023 = src.read(1)

# Simplify to a binary view for this map: vegetated (2 or 3) vs degraded/bare (1) vs water (0)
def simplify(arr):
    out = np.full(arr.shape, -1, dtype=np.int16)
    out[arr == 0] = 0   # water
    out[arr == 1] = 1   # bare/degraded
    out[(arr == 2) | (arr == 3)] = 2  # vegetated (either density)
    return out

s1990 = simplify(c1990)
s2023 = simplify(c2023)

valid = (s1990 >= 0) & (s2023 >= 0)

# Change categories:
# 0 = Water (either year)
# 1 = Persistently Degraded (bare in both)
# 2 = Newly Degraded (vegetated 1990 -> bare 2023)
# 3 = Recovered (bare 1990 -> vegetated 2023)
# 4 = Persistently Vegetated (vegetated in both)
change = np.full(s1990.shape, -1, dtype=np.int16)
change[valid & ((s1990 == 0) | (s2023 == 0))] = 0
change[valid & (s1990 == 1) & (s2023 == 1)] = 1
change[valid & (s1990 == 2) & (s2023 == 1)] = 2
change[valid & (s1990 == 1) & (s2023 == 2)] = 3
change[valid & (s1990 == 2) & (s2023 == 2)] = 4

CLASS_NAMES = {0: "Water", 1: "Persistently Degraded", 2: "Newly Degraded",
               3: "Recovered", 4: "Persistently Vegetated"}
PIXEL_AREA_KM2 = (30 * 30) / 1_000_000

print("Change category breakdown (1990 -> 2023):")
for code, name in CLASS_NAMES.items():
    count = np.sum(change == code)
    print(f"  {name}: {count * PIXEL_AREA_KM2:.2f} km^2")

out_profile = profile.copy()
out_profile.update(count=1, dtype="int16", nodata=-1)
with rasterio.open("data/classified/change_category.tif", "w", **out_profile) as dst:
    dst.write(change, 1)

COLORS = ["#2166ac", "#7f0000", "#f4a582", "#92c5de", "#1a9850"]
LABELS = list(CLASS_NAMES.values())
cmap = ListedColormap(COLORS)

fig, ax = plt.subplots(figsize=(10, 8))
display = change.astype(float)
display[display == -1] = np.nan
ax.imshow(display, cmap=cmap, vmin=0, vmax=4)
ax.set_title("Ogoniland: Where Land Cover Changed, 1990-2023", fontsize=14)
ax.axis("off")

patches = [mpatches.Patch(color=c, label=l) for c, l in zip(COLORS, LABELS)]
ax.legend(handles=patches, loc="lower left", fontsize=9, framealpha=0.9)

plt.tight_layout()
plt.savefig("data/classified/change_map.png", dpi=150, bbox_inches="tight")
print("\nSaved: data/classified/change_map.png")
