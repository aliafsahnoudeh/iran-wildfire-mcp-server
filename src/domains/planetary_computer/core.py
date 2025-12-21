from typing import Tuple

import planetary_computer as pc
import rasterio
from pystac_client import Client
from rasterio.warp import transform

TREE_COVER = 10
SHRUBLAND = 20
GRASSLAND = 30
CROPLAND = 40  # not considered burnable

BURNABLE = {TREE_COVER, SHRUBLAND, GRASSLAND}


import numpy as np

# ESA WorldCover classes
TREE_COVER = 10
SHRUBLAND = 20
GRASSLAND = 30

BURNABLE_NATURAL = {
    TREE_COVER,
    SHRUBLAND,
    GRASSLAND,
}


def is_wildfire_fuel_potential(
    lat: float,
    lon: float,
    window_size: int = 11,
    min_ratio: float = 0.4,
) -> Tuple[bool, float]:
    """
    Returns:
      (fuel_possible, burnable_ratio)

    fuel_possible=True means:
      natural vegetation exists AND wildfire can realistically spread.
    """

    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=pc.sign_inplace,
    )

    search = catalog.search(
        collections=["esa-worldcover"],
        intersects={"type": "Point", "coordinates": [lon, lat]},
    )

    item = next(search.items())
    asset = item.assets.get("map") or next(iter(item.assets.values()))
    href = asset.href

    with rasterio.open(href) as ds:
        xs, ys = transform("EPSG:4326", ds.crs, [lon], [lat])
        x, y = xs[0], ys[0]
        row, col = ds.index(x, y)

        half = window_size // 2
        window = rasterio.windows.Window(
            col - half,
            row - half,
            window_size,
            window_size,
        )

        data = ds.read(1, window=window, boundless=True, fill_value=0)

    total_pixels = data.size
    burnable_pixels = np.sum(np.isin(data, list(BURNABLE_NATURAL)))
    ratio = burnable_pixels / total_pixels

    fuel_possible = ratio >= min_ratio
    return fuel_possible, round(float(ratio), 3)
