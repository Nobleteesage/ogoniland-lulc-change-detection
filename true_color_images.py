import rasterio
import numpy as np
import matplotlib.pyplot as plt

EPOCHS = ["1990", "2010", "2023"]
NODATA = -32768


def stretch(band, valid, lower_pct=2, upper_pct=98):
    vals = band[valid]
    lo, hi = np.percentile(vals, [lower_pct, upper_pct])
    stretched = np.clip((band - lo) / (hi - lo + 1e-6), 0, 1)
    return stretched


fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, epoch in zip(axes, EPOCHS):
    with rasterio.open(f"data/raw/ogoniland_{epoch}.tif") as src:
        red = src.read(1).astype(np.float32)
        green = src.read(2).astype(np.float32)
        blue = src.read(3).astype(np.float32)

    valid = red != NODATA

    r = stretch(red, valid)
    g = stretch(green, valid)
    b = stretch(blue, valid)

    rgb = np.dstack([r, g, b])
    rgb_display = rgb.copy()
    rgb_display[~valid] = 1.0  # show no-data corners as white

    ax.imshow(rgb_display)
    ax.set_title(f"Ogoniland {epoch} (true color)", fontsize=14)
    ax.axis("off")

    plt.imsave(f"data/classified/ogoniland_{epoch}_truecolor.png", rgb_display)

plt.tight_layout()
plt.savefig("data/classified/truecolor_comparison.png", dpi=150, bbox_inches="tight")
print("Saved 3 individual true-color images and truecolor_comparison.png")
