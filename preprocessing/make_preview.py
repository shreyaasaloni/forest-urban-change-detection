from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import rasterio

Path("outputs").mkdir(exist_ok=True)
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

for ax, year in zip(axes, (2020, 2025)):
    with rasterio.open(f"data/processed/s2_{year}_processed.tif") as src:
        rgb = src.read([3, 2, 1])          # Red, Green, Blue
    nodata = np.any(rgb == -9999, axis=0)
    img = np.clip(rgb / 0.3, 0, 1)         # brighten for display
    img = np.moveaxis(img, 0, -1)
    img[nodata] = 1                        # show no-data as white
    ax.imshow(img)
    ax.set_title(f"West Hyderabad, {year}")
    ax.axis("off")

plt.tight_layout()
plt.savefig("outputs/hyderabad_comparison.png", dpi=200)
print("Saved: outputs/hyderabad_comparison.png")