# https://console.cloud.google.com/earth-engine/welcome

from __future__ import annotations

import datetime as dt
import os
from typing import Optional

import pandas as pd
from dotenv import load_dotenv

try:
    import ee  # type: ignore
except ImportError:  # GEE is optional
    ee = None


load_dotenv()
GOOGLE_EARTH_ENGINE_PROJECT = os.getenv("GOOGLE_EARTH_ENGINE_PROJECT")


def init_earth_engine(
    service_account: Optional[str] = None,
    key_path: Optional[str] = None,
    project: Optional[str] = GOOGLE_EARTH_ENGINE_PROJECT,
) -> None:
    """
    Initialize Google Earth Engine.

    You can either:

    - Use saved user credentials (after running `earthengine authenticate` once):
        init_earth_engine(project='your-project-id')
    - Or use a service account:
        init_earth_engine(service_account='xxx@project.iam.gserviceaccount.com',
                          key_path='path/to/key.json',
                          project='your-project-id')

    Requires:
        pip install earthengine-api
        and a registered Earth Engine account / project.
    """
    if ee is None:
        raise ImportError(
            "earthengine-api is not installed. pip install earthengine-api"
        )

    if service_account and key_path:
        credentials = ee.ServiceAccountCredentials(service_account, key_path)
        ee.Initialize(credentials, project=project)
    else:
        # Will use default credentials (user or default service account)
        ee.Initialize(project=project)


def _ensure_ee_initialized() -> None:
    if ee is None:
        raise ImportError("earthengine-api is not installed.")
    # Simple check; will raise if not authenticated
    try:
        _ = ee.Image().bandNames()
    except Exception as exc:  # pragma: no cover - only runtime check
        raise RuntimeError(
            "Earth Engine is not initialized. Call init_earth_engine() first."
        ) from exc


#   ESA WorldCover land cover class at a point
#   Dataset: ESA/WorldCover/v200 (band: "Map")
WORLD_COVER_COLLECTION_ID = "ESA/WorldCover/v200"


def get_worldcover_class(
    latitude: float,
    longitude: float,
    year: int = 2021,
    scale: int = 10,
) -> Optional[int]:
    """
    Get ESA WorldCover land cover class at given point.

    Parameters
    ----------
    latitude, longitude:
        Location in WGS84.
    year:
        WorldCover year (2020 or 2021). The v200 collection only has 2021 data.
    scale:
        Sampling scale in meters (10 is the native resolution).

    Returns
    -------
    int or None
        Land cover class code at the point, or None if sampling fails.

    Notes
    -----
    See ESA WorldCover docs for class legend.
    ESA WorldCover v200 is the latest free version and only covers 2021.
    For the most updated land cover data, 2021 is the latest available.
    """
    _ensure_ee_initialized()

    # ESA WorldCover v200 ImageCollection contains 2021 data
    # Use ImageCollection and .first() as shown in official docs
    collection = ee.ImageCollection(WORLD_COVER_COLLECTION_ID)
    image = collection.first()

    point = ee.Geometry.Point([longitude, latitude])

    # Sample the image at the point location using reduceRegion
    sampled = image.reduceRegion(
        reducer=ee.Reducer.first(), geometry=point, scale=scale
    ).getInfo()

    if sampled is None or "Map" not in sampled:
        return None

    value = sampled.get("Map")
    if value is None:
        return None
    return int(value)


# MODIS NDVI time series (MODIS/061/MOD13Q1, band "NDVI")

MODIS_NDVI_COLLECTION_ID = "MODIS/061/MOD13Q1"


def get_modis_ndvi_timeseries(
    latitude: float,
    longitude: float,
    start: dt.date,
    end: dt.date,
    scale: int = 250,
) -> pd.DataFrame:
    """
    Get a MODIS NDVI time series for a point using GEE.

    Parameters
    ----------
    latitude, longitude:
        Location in WGS84.
    start, end:
        Date range for NDVI images.
    scale:
        Spatial resolution in meters (250 m native).

    Returns
    -------
    pandas.DataFrame
        Columns: ["time", "ndvi"], where time is UTC datetime64[ns].

    Notes
    -----
    NDVI in MOD13Q1 is scaled (usually by 1e4). You may want to rescale:
        ndvi_float = df["ndvi"] / 1e4
    """
    _ensure_ee_initialized()

    point = ee.Geometry.Point([longitude, latitude])
    collection = (
        ee.ImageCollection(MODIS_NDVI_COLLECTION_ID)
        .filterDate(start.isoformat(), end.isoformat())
        .select("NDVI")
    )

    # Check if collection is empty before calling getRegion
    collection_size = collection.size().getInfo()
    if collection_size == 0:
        return pd.DataFrame(columns=["time", "ndvi"])

    # getRegion returns rows: [id, lat, lon, time, NDVI]
    region = collection.getRegion(point, scale).getInfo()

    if len(region) <= 1:
        return pd.DataFrame(columns=["time", "ndvi"])

    header = region[0]
    rows = region[1:]
    time_idx = header.index("time")
    ndvi_idx = header.index("NDVI")

    records = []
    for row in rows:
        try:
            ts_ms = row[time_idx]
            value = row[ndvi_idx]
        except (IndexError, KeyError):
            continue
        if value is None:
            continue
        # GEE timestamps are in milliseconds since epoch
        ts = dt.datetime.utcfromtimestamp(ts_ms / 1000.0)
        records.append({"time": ts, "ndvi": value})

    df = pd.DataFrame.from_records(records)
    df.sort_values("time", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# Fire Weather Index from GFWED (ce-merra2_fwi-daily)
# NOTE: This dataset requires Climate Engine Pro subscription and is NOT available
# with free Google Earth Engine accounts.
GFWED_FWI_COLLECTION_ID = "projects/climate-engine-pro/assets/ce-merra2_fwi-daily"


def get_gfwed_fwi_timeseries(
    latitude: float,
    longitude: float,
    start: dt.date,
    end: dt.date,
    scale: int = 50000,
) -> pd.DataFrame:
    """
    Get Fire Weather Index (FWI) time series from GFWED via GEE.

    WARNING: This function requires a Climate Engine Pro subscription.
    It will not work with free Google Earth Engine accounts.

    Parameters
    ----------
    latitude, longitude:
        Location in WGS84.
    start, end:
        Date range for FWI.
    scale:
        Spatial scale in meters (~50 km native).

    Returns
    -------
    pandas.DataFrame
        Columns: ["time", "FWI"].
        Returns empty DataFrame if dataset is not accessible.
    """
    _ensure_ee_initialized()

    try:
        point = ee.Geometry.Point([longitude, latitude])
        collection = (
            ee.ImageCollection(GFWED_FWI_COLLECTION_ID)
            .filterDate(start.isoformat(), end.isoformat())
            .select("FWI")
        )

        # Check if collection is empty before calling getRegion
        collection_size = collection.size().getInfo()
        if collection_size == 0:
            return pd.DataFrame(columns=["time", "FWI"])

        region = collection.getRegion(point, scale).getInfo()

        if len(region) <= 1:
            return pd.DataFrame(columns=["time", "FWI"])

        header = region[0]
        rows = region[1:]
        time_idx = header.index("time")
        fwi_idx = header.index("FWI")

        records = []
        for row in rows:
            try:
                ts_ms = row[time_idx]
                value = row[fwi_idx]
            except (IndexError, KeyError):
                continue
            if value is None:
                continue
            ts = dt.datetime.utcfromtimestamp(ts_ms / 1000.0)
            records.append({"time": ts, "FWI": float(value)})

        df = pd.DataFrame.from_records(records)
        df.sort_values("time", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except Exception as e:
        # Dataset not accessible (requires Climate Engine Pro subscription)
        import warnings

        warnings.warn(
            f"GFWED Fire Weather Index dataset not accessible: {str(e)}. "
            "This dataset requires Climate Engine Pro subscription. "
            "Returning empty DataFrame.",
            UserWarning,
        )
        return pd.DataFrame(columns=["time", "FWI"])
