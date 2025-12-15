import datetime as dt
from typing import Any, Dict, Iterable, Optional

import requests

from .types import RawOpenMeteoCurrent, RawOpenMeteoForecast, RawOpenMeteoHourly

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_open_meteo_forecast(
    latitude: float,
    longitude: float,
    hourly: Iterable[str] = (
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
    ),
    current: Iterable[str] = ("temperature_2m", "wind_speed_10m"),
    start: Optional[dt.date] = None,
    end: Optional[dt.date] = None,
    timezone: str = "UTC",
    timeout: int = 30,
) -> RawOpenMeteoForecast:
    """
    Fetch weather forecast / recent history from Open-Meteo.

    Parameters
    ----------
    latitude, longitude:
        Point of interest.
    hourly:
        List of hourly variables to request.
        See docs for full list of supported variables.
    current:
        List of current weather variables.
    start, end:
        Optional date range (YYYY-MM-DD). If omitted, Open-Meteo chooses default.
    timezone:
        Timezone string, e.g. "UTC" or "auto".
    timeout:
        HTTP timeout in seconds.

    Returns
    -------
    RawOpenMeteoForecast
        Parsed and structured Open-Meteo forecast response.
    """
    params: Dict[str, Any] = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(hourly),
        "current": ",".join(current),
        "timezone": timezone,
    }

    if start is not None:
        params["start_date"] = start.isoformat()
    if end is not None:
        params["end_date"] = end.isoformat()

    resp = requests.get(OPEN_METEO_FORECAST_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    # Parse nested structures into dataclasses
    current = data.get("current", {})
    hourly = data.get("hourly", {})

    raw_current = RawOpenMeteoCurrent(
        time=current.get("time", ""),
        interval=current.get("interval", 0),
        temperature_2m=current.get("temperature_2m", 0.0),
        wind_speed_10m=current.get("wind_speed_10m", 0.0),
    )

    raw_hourly = RawOpenMeteoHourly(
        time=hourly.get("time", []),
        temperature_2m=hourly.get("temperature_2m", []),
        wind_speed_10m=hourly.get("wind_speed_10m", []),
        precipitation=hourly.get("precipitation", []),
        relative_humidity_2m=hourly.get("relative_humidity_2m", []),
    )

    return RawOpenMeteoForecast(
        latitude=data.get("latitude", 0.0),
        longitude=data.get("longitude", 0.0),
        generationtime_ms=data.get("generationtime_ms", 0.0),
        utc_offset_seconds=data.get("utc_offset_seconds", 0),
        timezone=data.get("timezone", ""),
        timezone_abbreviation=data.get("timezone_abbreviation", ""),
        elevation=data.get("elevation", 0.0),
        current_units=data.get("current_units", {}),
        current=raw_current,
        hourly_units=data.get("hourly_units", {}),
        hourly=raw_hourly,
    )
