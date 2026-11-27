from pathlib import Path
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

RAW = Path("data/raw")
OUT = Path("data/processed")
YEARS = [2020, 2025]
BANDS = ["B2", "B3", "B4", "B8", "B11"]
NODATA = -9999.0


def read_aligned(path, ref):
    with rasterio.open(path) as src:
        if src.count != len(BANDS) or src.crs is None:
            raise ValueError(f"{path}: need {len(BANDS)} bands and a CRS")
        with WarpedVRT(src, crs=ref["crs"], transform=ref["transform"],
                       width=ref["width"], height=ref["height"],
                       resampling=Resampling.bilinear,
                       src_nodata=0, nodata=0) as vrt:
            return vrt.read().astype("float32")


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # The first year defines the grid
    with rasterio.open(RAW / f"s2_{YEARS[0]}.tif") as src:
        ref = src.profile.copy()

    images = {y: read_aligned(RAW / f"s2_{y}.tif", ref) for y in YEARS}

    # Keep only pixels that are valid in every band and both years
    valid = np.logical_and.reduce(
        [np.all(np.isfinite(a) & (a > 0), axis=0) for a in images.values()]
    )

    ref.update(driver="GTiff", count=len(BANDS), dtype="float32",
               nodata=NODATA, compress="deflate")

    for year, a in images.items():
        result = np.where(valid, np.clip(a / 10000, 0, 1), NODATA).astype("float32")
        path = OUT / f"s2_{year}_processed.tif"
        with rasterio.open(path, "w", **ref) as dst:
            dst.write(result)
            for i, name in enumerate(BANDS, start=1):
                dst.set_band_description(i, name)
        print("Saved:", path)

    print(f"Valid pixels: {valid.mean() * 100:.1f}%")


if __name__ == "__main__":
    main()