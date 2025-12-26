from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

from .types import AirPollutionResponse, ForecastResponse, ReverseGeocodingResponse

OPENWEATHER_BASE_URL = "https://api.openweathermap.org"
OPENWEATHER_ONECALL_URL = f"{OPENWEATHER_BASE_URL}/data/2.5/forecast"
OPENWEATHER_AIR_POLLUTION_URL = f"{OPENWEATHER_BASE_URL}/data/2.5/air_pollution"
OPENWEATHER_REVERSE_GEOCODING_URL = f"{OPENWEATHER_BASE_URL}/geo/1.0/reverse"

load_dotenv()


def _get_api_key(api_key: Optional[str] = None) -> str:
    """Get API key from parameter or environment variable.

    Args:
        api_key: Optional API key to use

    Returns:
        str: The API key

    Raises:
        ValueError: If no API key is provided or found in environment
    """
    if api_key is None:
        api_key = os.environ.get("OPEN_WEATHER_MAP_API_KEY")
        if api_key is None:
            raise ValueError(
                "API key must be provided or set in OPEN_WEATHER_MAP_API_KEY environment variable"
            )
    return api_key


# TODO: pass the full list of parameters to the function
def get_openweather_onecall(
    latitude: float,
    longitude: float,
    api_key: str | None = None,
    timeout: int = 30,
) -> ForecastResponse:
    """
    You can search weather forecast for 5 days with data every 3 hours by geographic coordinates.
    All weather data can be obtained in JSON and XML formats.

    Parameters:
        latitude	required	Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
        longitude	required	Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
        api_key	optional	Your unique API key (you can always find it on your account page under the "API key" tab). If not provided, will use OPEN_WEATHER_MAP_API_KEY environment variable.
        units	optional	Units of measurement. standard, metric and imperial units are available. If you do not use the units parameter, standard units will be applied by default. Learn more
        mode	optional	Response format. JSON format is used by default. To get data in XML format use mode=xml. Learn more
        cnt	optional	A number of timestamps, which will be returned in the API response. Learn more
        units	optional	Units of measurement. standard, metric and imperial units are available. If you do not use the units parameter, standard units will be applied by default. Learn more
        lang	optional	You can use the lang parameter to get the output in your language. Learn more
        timeout	optional	Request timeout in seconds (default is 30 seconds)

    Returns:
    ForecastResponse
    """
    api_key = _get_api_key(api_key)

    params: Dict[str, Any] = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
    }

    resp = requests.get(OPENWEATHER_ONECALL_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    json_response = resp.json()
    return ForecastResponse.from_dict(json_response)


# TODO: pass the full list of parameters to the function
def get_current_air_pollution_data(
    latitude: float,
    longitude: float,
    api_key: str | None = None,
    timeout: int = 30,
) -> AirPollutionResponse:
    """
    Air Pollution API provides current and forecast air pollution data for any coordinates on the globe.

    Parameters:
    lat	required	Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
    lon	required	Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
    appid	optional	Your unique API key (you can always find it on your account page under the "API key" tab). If not provided, will use OPEN_WEATHER_MAP_API_KEY environment variable.

    Returns:
    AirPollutionResponse
    """
    api_key = _get_api_key(api_key)

    params: Dict[str, Any] = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
    }

    resp = requests.get(OPENWEATHER_AIR_POLLUTION_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    json_response = resp.json()
    return AirPollutionResponse.from_dict(json_response)


# TODO: pass the full list of parameters to the function
def get_historical_air_pollution_data(
    latitude: float,
    longitude: float,
    start: int,
    end: int,
    api_key: str | None = None,
    timeout: int = 30,
) -> AirPollutionResponse:
    """
    Air Pollution API provides historical air pollution data for any coordinates on the globe.

    Official documentation: https://openweathermap.org/api/air-pollution

    Parameters:
    lat	required	Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
    lon	required	Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
    start	required	Start date (unix time, UTC time zone), e.g. start=1606488670
    end	required	End date (unix time, UTC time zone), e.g. end=1606747870
    appid	optional	Your unique API key (you can always find it on your account page under the "API key" tab). If not provided, will use OPEN_WEATHER_MAP_API_KEY environment variable.

    Returns:
    AirPollutionResponse
    """
    api_key = _get_api_key(api_key)

    params: Dict[str, Any] = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
        "start": start,
        "end": end,
    }

    resp = requests.get(
        OPENWEATHER_AIR_POLLUTION_URL + "/history", params=params, timeout=timeout
    )
    resp.raise_for_status()
    json_response = resp.json()
    return AirPollutionResponse.from_dict(json_response)


def get_reverse_geocoding(
    latitude: float,
    longitude: float,
    api_key: str | None = None,
    limit: int = 1,
    timeout: int = 30,
) -> ReverseGeocodingResponse:
    """
    Reverse geocoding allows to get name of the location (city name or area name) by using geografical coordinates (lat, lon).
    The limit parameter in the API call allows you to cap how many location names you will see in the API response.


    Parameters:
    lat, lon	required	Geographical coordinates (latitude, longitude)
    api_key	optional	Your unique API key (you can always find it on your account page under the "API key" tab). If not provided, will use OPEN_WEATHER_MAP_API_KEY environment variable.
    limit	optional	Number of the location names in the API response (several results can be returned in the API response)
    timeout	optional	Request timeout in seconds (default is 30 seconds)

    Returns:
    ReverseGeocodingResponse

    """
    api_key = _get_api_key(api_key)

    params: Dict[str, Any] = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
        "limit": limit,
    }
    resp = requests.get(
        OPENWEATHER_REVERSE_GEOCODING_URL, params=params, timeout=timeout
    )
    resp.raise_for_status()
    json_response = resp.json()
    return ReverseGeocodingResponse.from_dict(json_response)
