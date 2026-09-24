import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

with rasterio.open("data/classified/ogoniland_2010_final.tif") as src:
    c2010 = src.read(1)
    profile = src.profile

with rasterio.open("data/classified/ogoniland_2023_final.tif") as src:
    c2023 = src.read(1)


def simplify(arr):
    out = np.full(arr.shape, -1, dtype=np.int16)
    out[arr == 0] = 0
    out[arr == 1] = 1
    out[(arr == 2) | (arr == 3)] = 2
    return out


s2010 = simplify(c2010)
s2023 = simplify(c2023)
valid = (s2010 >= 0) & (s2023 >= 0)

change = np.full(s2010.shape, -1, dtype=np.int16)
change[valid & ((s2010 == 0) | (s2023 == 0))] = 0
change[valid & (s2010 == 1) & (s2023 == 1)] = 1
change[valid & (s2010 == 2) & (s2023 == 1)] = 2
change[valid & (s2010 == 1) & (s2023 == 2)] = 3
change[valid & (s2010 == 2) & (s2023 == 2)] = 4

CLASS_NAMES = {0: "Water", 1: "Persistently Degraded", 2: "Newly Degraded",
               3: "Recovered", 4: "Persistently Vegetated"}
PIXEL_AREA_KM2 = (30 * 30) / 1_000_000

print("Change category breakdown (2010 -> 2023):")
for code, name in CLASS_NAMES.items():
    count = np.sum(change == code)
    print(f"  {name}: {count * PIXEL_AREA_KM2:.2f} km^2")

out_profile = profile.copy()
out_profile.update(count=1, dtype="int16", nodata=-1)
with rasterio.open("data/classified/change_category_2010_2023.tif", "w", **out_profile) as dst:
    dst.write(change, 1)

COLORS = ["#2166ac", "#7f0000", "#f4a582", "#92c5de", "#1a9850"]
LABELS = list(CLASS_NAMES.values())
cmap = ListedColormap(COLORS)

fig, ax = plt.subplots(figsize=(10, 8))
display = change.astype(float)
display[display == -1] = np.nan
ax.imshow(display, cmap=cmap, vmin=0, vmax=4)
ax.set_title("Ogoniland: Post-Assessment Recovery, 2010-2023", fontsize=14)
ax.axis("off")

patches = [mpatches.Patch(color=c, label=l) for c, l in zip(COLORS, LABELS)]
ax.legend(handles=patches, loc="lower left", fontsize=9, framealpha=0.9)

plt.tight_layout()
plt.savefig("data/classified/change_map_2010_2023.png", dpi=150, bbox_inches="tight")
print("\nSaved: data/classified/change_map_2010_2023.png")
