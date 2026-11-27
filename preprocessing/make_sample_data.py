from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_origin

out = Path("data/raw")
out.mkdir(parents=True, exist_ok=True)

for year in (2020, 2025):
    path = out / f"s2_{year}.tif"
    if path.exists():
        print("Already exists, skipped:", path)
        continue
    data = np.random.randint(200, 4000, (5, 200, 200)).astype("uint16")
    with rasterio.open(path, "w", driver="GTiff", height=200, width=200,
                       count=5, dtype="uint16", crs="EPSG:32643", nodata=0,
                       transform=from_origin(780000, 1440000, 10, 10)) as dst:
        dst.write(data)
    print("Created:", path)