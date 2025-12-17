import logging
import os
from datetime import datetime
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from is_in_iran import is_in_iran

from .types import RawFireData

# Development mode
FIRE_DEV_MODE = os.getenv("FIRE_DEV_MODE", "1") == "1"

logger = logging.getLogger(__name__)

if FIRE_DEV_MODE:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )

# Larger bbox around Iran
IRAN_BBOX = {"lat_min": 23.69, "lat_max": 40.06, "lon_min": 43.39, "lon_max": 64.27}


def _build_bbox() -> str:
    """Return bbox string like 'lon_min,lat_min,lon_max,lat_max'."""
    return (
        f"{IRAN_BBOX['lon_min']},{IRAN_BBOX['lat_min']},"
        f"{IRAN_BBOX['lon_max']},{IRAN_BBOX['lat_max']}"
    )


def _resolve_api_key(api_key: Optional[str]) -> str:
    """Resolve API key from argument or environment."""
    if api_key is not None:
        return api_key

    load_dotenv()
    key = os.getenv("FIRMS_API_KEY")
    if not key:
        raise ValueError(
            "FIRMS_API_KEY is missing. "
            "Pass api_key manually or set FIRMS_API_KEY in a .env file."
        )
    return key


def _build_firms_url(
    api_key: str, bbox: str, start_date: Optional[str], end_date: Optional[str]
) -> str:
    """Build the FIRMS CSV API request URL."""
    base = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
    product = "VIIRS_NOAA20_NRT"

    if start_date and end_date:
        d0 = datetime.strptime(start_date, "%Y-%m-%d")
        d1 = datetime.strptime(end_date, "%Y-%m-%d")
        day_range = (d1 - d0).days + 1
        if day_range < 1:
            raise ValueError("end_date must be after or equal to start_date")
        logger.info(f"Range mode: {start_date} → {end_date} ({day_range} days)")
        return f"{base}/{api_key}/{product}/{bbox}/{day_range}/{start_date}"

    if start_date:
        logger.info(f"Single-day mode: {start_date}")
        return f"{base}/{api_key}/{product}/{bbox}/1/{start_date}"

    logger.info("Default mode: last day only")
    return f"{base}/{api_key}/{product}/{bbox}/1"


def get_fires_in_iran(
    api_key: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    frp: float = 10,
    bright_ti4: float = 330,
) -> list[RawFireData]:
    """
    Query NASA FIRMS for fire detections inside Iran.
    Filters by:
        - api_key (optional)
        - Date range (using start_date and end_date)
        - frp: Fire Radiative Power (MW) greater than frp
        - bright_ti4: Brightness temperature (Kelvin) in MODIS/VIIRS band I5/T5
        greater than bright_ti4

    Returns a list of RawFireData with filtered fires.
    """
    key = _resolve_api_key(api_key)
    bbox = _build_bbox()
    url = _build_firms_url(key, bbox, start_date, end_date)

    if FIRE_DEV_MODE:
        logger.info(f"Requesting FIRMS CSV: {url}")

    df = pd.read_csv(url)

    if FIRE_DEV_MODE:
        logger.info(f"Retrieved {len(df)} raw fire records")

    # Apply filtering
    mask = (
        df.apply(lambda r: is_in_iran(r["latitude"], r["longitude"]), axis=1)
        & (df["frp"] > frp)
        & (df["bright_ti4"] > bright_ti4)
    )

    filtered = df[mask].reset_index(drop=True)

    if FIRE_DEV_MODE:
        logger.info(f"Detected {len(filtered)} fires within Iran above thresholds")

    fires = [
        RawFireData(
            latitude=row["latitude"],
            longitude=row["longitude"],
            bright_ti4=row["bright_ti4"],
            scan=row["scan"],
            track=row["track"],
            acq_date=row["acq_date"],
            acq_time=row["acq_time"],
            satellite=row["satellite"],
            instrument=row["instrument"],
            confidence=row["confidence"],
            version=row["version"],
            bright_ti5=row["bright_ti5"],
            frp=row["frp"],
            daynight=row["daynight"],
        )
        for _, row in filtered.iterrows()
    ]
    return sorted(fires, key=lambda x: x.latitude)
