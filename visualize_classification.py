import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

EPOCHS = ["1990", "2010", "2023"]
COLORS = ["#2166ac", "#b2182b", "#fee08b", "#1a9850"]  # Water, Bare, Moderate Veg, Dense Veg
LABELS = ["Water", "Bare/Built-up/Degraded", "Moderate Vegetation", "Dense Vegetation/Mangrove"]

cmap = ListedColormap(COLORS)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, epoch in zip(axes, EPOCHS):
    with rasterio.open(f"data/classified/ogoniland_{epoch}_final.tif") as src:
        data = src.read(1).astype(float)
        data[data == -1] = np.nan

    ax.imshow(data, cmap=cmap, vmin=0, vmax=3)
    ax.set_title(f"Ogoniland {epoch}", fontsize=14)
    ax.axis("off")

patches = [mpatches.Patch(color=c, label=l) for c, l in zip(COLORS, LABELS)]
fig.legend(handles=patches, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.05))

plt.tight_layout()
plt.savefig("data/classified/comparison_map.png", dpi=150, bbox_inches="tight")
print("Saved: data/classified/comparison_map.png")
