from datetime import datetime, timedelta
from typing import Optional

from mcp.server.fastmcp import FastMCP

from src.domains.google_earth_engine.core import (
    get_gfwed_fwi_timeseries,
    get_modis_ndvi_timeseries,
    get_worldcover_class,
    init_earth_engine,
)
from src.domains.nasa_firms.core import get_fires_in_iran
from src.domains.open_weather_map.core import (
    get_current_air_pollution_data,
    get_historical_air_pollution_data,
    get_openweather_onecall,
    get_reverse_geocoding,
)

mcp = FastMCP("iran_wildfire")


@mcp.tool()
async def get_iran_wildfires_by_day(
    date: Optional[str] = None,
    frp: float = 10,
    bright_ti4: float = 330,
) -> str:
    """
    Returns fire detections inside Iran in one specific day combining all other available mcp tools.

    """
    response = get_fires_in_iran(
        start_date=date,
        end_date=date,
        frp=frp,
        bright_ti4=bright_ti4,
    )

    # Convert date string to datetime and calculate timestamps
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    end_timestamp = int(date_obj.timestamp())
    start_date_obj = date_obj - timedelta(days=7)
    start_timestamp = int(start_date_obj.timestamp())

    init_earth_engine()

    output = ["List of wildfires detected in Iran:\n"]

    for i, fire in enumerate(response, 1):
        # TODO test
        if i > 5:
            break
        address = get_reverse_geocoding(
            latitude=fire.latitude,
            longitude=fire.longitude,
        )
        output.append(str(i) + ". Fire Detected:\n")
        output.append(address.to_human_readable(address))  # type: ignore
        output.append(20 * "=")

        output.append("NASA FIRMS Data:")
        output.append(fire.to_human_readable())  # type: ignore
        output.append(20 * "=" + "\n")

        output.append("OpenWeather OneCall Data:\n")
        openweather_result = get_openweather_onecall(
            latitude=fire.latitude,
            longitude=fire.longitude,
        )
        output.append(openweather_result.to_human_readable())  # type: ignore

        output.append(20 * "-" + "")
        output.append("Current Air Pollution Data:\n")
        current_air_pollution = get_current_air_pollution_data(
            latitude=fire.latitude,
            longitude=fire.longitude,
        )
        output.append(current_air_pollution.to_human_readable())  # type: ignore

        ndvi_timeseries = get_modis_ndvi_timeseries(
            latitude=fire.latitude,
            longitude=fire.longitude,
            start=start_date_obj.date(),
            end=date_obj.date(),
        )
        output.append(f"MODIS NDVI timeseries: {ndvi_timeseries.__str__()}")

        fwi_timeseries = get_gfwed_fwi_timeseries(
            latitude=fire.latitude,
            longitude=fire.longitude,
            start=start_date_obj.date(),
            end=date_obj.date(),
        )
        output.append(f"GFWED FWI timeseries: {fwi_timeseries.__str__()}")

        worldcover_class_2021 = get_worldcover_class(
            latitude=fire.latitude, longitude=fire.longitude
        )

        if worldcover_class_2021 is not None:
            output.append(
                f"WorldCover 2021 Land Cover Class: {worldcover_class_2021.__str__()}"
            )

        output.append("\n\nHistorical Air Pollution Data (last 7 days):\n")

        historical_air_pollution_data = get_historical_air_pollution_data(
            latitude=fire.latitude,
            longitude=fire.longitude,
            start=start_timestamp,
            end=end_timestamp,
        )
        output.append(historical_air_pollution_data.to_human_readable())  # type: ignore

    return "\n".join(output)


@mcp.tool()
async def reverse_geocoding(
    latitude: float,
    longitude: float,
    api_key: Optional[str] = None,
    limit: int = 1,
    timeout: int = 30,
) -> str:
    """
    Reverse geocoding allows to get name of the location (city name or area name) by using geografical coordinates (lat, lon).
    The limit parameter in the API call allows you to cap how many location names you will see in the API response.


    Parameters:
    lat, lon	required	Geographical coordinates (latitude, longitude)
    appid	optional	Your unique API key (you can always find it on your account page under the "API key" tab). If not provided, will use OPEN_WEATHER_MAP_API_KEY environment variable.
    limit	optional	Number of the location names in the API response (several results can be returned in the API response)

    Returns:
    str

    """
    response = get_reverse_geocoding(
        latitude=latitude,
        longitude=longitude,
        api_key=api_key,
        limit=limit,
        timeout=timeout,
    )
    return response.to_human_readable(response)  # type: ignore


@mcp.tool()
async def nasa_frims_fires_in_iran(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    frp: float = 10,
    bright_ti4: float = 330,
) -> str:
    """
    Query NASA FIRMS for fire detections inside Iran.
    """
    response = get_fires_in_iran(
        start_date=start_date,
        end_date=end_date,
        frp=frp,
        bright_ti4=bright_ti4,
    )

    return "Fires detected by NASA FIRMS:\n\n" + "".join(
        [fire.to_human_readable(i) for i, fire in enumerate(response, 1)]
    )


@mcp.tool()
async def openweather_onecall_data(
    latitude: float,
    longitude: float,
    api_key: Optional[str] = None,
    exclude: Optional[str] = None,
    units: str = "metric",
    lang: str = "en",
    timeout: int = 30,
) -> str:
    """
    You can search weather forecast for 5 days with data every 3 hours by geographic coordinates.
    All weather data can be obtained in JSON and XML formats.

    Parameters:
    latitude	required	Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
    longitude	required	Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API

    """
    response = get_openweather_onecall(
        latitude=latitude,
        longitude=longitude,
        api_key=api_key,
        timeout=timeout,
    )
    return response.to_human_readable()  # type: ignore


@mcp.tool()
async def current_air_pollution_data(
    latitude: float,
    longitude: float,
    api_key: Optional[str] = None,
    timeout: int = 30,
) -> str:
    """
    Air Pollution API provides current and forecast air pollution data for any coordinates on the globe.

    Parameters:
    latitude	required	Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
    longitude	required	Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API

    """
    response = get_current_air_pollution_data(
        latitude=latitude,
        longitude=longitude,
        api_key=api_key,
        timeout=timeout,
    )
    return response.to_human_readable()  # type: ignore


@mcp.tool()
async def historical_air_pollution_data(
    latitude: float,
    longitude: float,
    start: int,  # Unix timestamp
    end: int,  # Unix timestamp
    api_key: Optional[str] = None,
    timeout: int = 30,
) -> str:
    """
    Air Pollution API provides historical air pollution data for any coordinates on the globe.

    Parameters:
    latitude	required	Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
    longitude	required	Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
    start	required	Start of the period (Unix timestamp)
    end	required	End of the period (Unix timestamp)

    """
    response = get_historical_air_pollution_data(
        latitude=latitude,
        longitude=longitude,
        start=start,
        end=end,
        api_key=api_key,
        timeout=timeout,
    )
    return response.to_human_readable()  # type: ignore


@mcp.tool()
async def modis_ndvi_timeseries(
    latitude: float,
    longitude: float,
    start_date: str,  # YYYY-MM-DD
    end_date: str,  # YYYY-MM-DD
    scale: int = 250,
) -> str:
    """
    Get MODIS NDVI (Normalized Difference Vegetation Index) time series for a point using Google Earth Engine.
    NDVI is a measure of vegetation health and density.

    Parameters:
    latitude	required	Latitude in WGS84
    longitude	required	Longitude in WGS84
    start_date	required	Start date for NDVI images (format: YYYY-MM-DD)
    end_date	required	End date for NDVI images (format: YYYY-MM-DD)
    scale	optional	Spatial resolution in meters (default: 250m native resolution)

    Returns:
    str: Time series data with columns: time, ndvi
    Note: NDVI values are scaled by 1e4 in the raw data
    """
    init_earth_engine()

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    # Add one day to end date to ensure the range includes the end date
    end = end + timedelta(days=1)

    df = get_modis_ndvi_timeseries(
        latitude=latitude,
        longitude=longitude,
        start=start,
        end=end,
        scale=scale,
    )

    if df.empty:
        return (
            "No MODIS NDVI data available for the specified location and time period."
        )

    return f"MODIS NDVI Time Series:\n{df.to_string()}"


@mcp.tool()
async def gfwed_fwi_timeseries(
    latitude: float,
    longitude: float,
    start_date: str,  # YYYY-MM-DD
    end_date: str,  # YYYY-MM-DD
    scale: int = 50000,
) -> str:
    """
    Get Fire Weather Index (FWI) time series from GFWED via Google Earth Engine.
    FWI is a numeric rating of fire danger based on weather conditions.

    WARNING: This requires a Climate Engine Pro subscription and will not work with free Google Earth Engine accounts.

    Parameters:
    latitude	required	Latitude in WGS84
    longitude	required	Longitude in WGS84
    start_date	required	Start date for FWI data (format: YYYY-MM-DD)
    end_date	required	End date for FWI data (format: YYYY-MM-DD)
    scale	optional	Spatial scale in meters (default: 50000m / ~50km native resolution)

    Returns:
    str: Time series data with columns: time, FWI
    """
    init_earth_engine()

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    # Add one day to end date to ensure the range includes the end date
    end = end + timedelta(days=1)

    df = get_gfwed_fwi_timeseries(
        latitude=latitude,
        longitude=longitude,
        start=start,
        end=end,
        scale=scale,
    )

    if df.empty:
        return "No GFWED FWI data available. This dataset requires Climate Engine Pro subscription."

    return f"GFWED Fire Weather Index Time Series:\n{df.to_string()}"


@mcp.tool()
async def worldcover_land_class(
    latitude: float,
    longitude: float,
    year: int = 2021,
    scale: int = 10,
) -> str:
    """
    Get ESA WorldCover land cover class at a given point using Google Earth Engine.
    Provides information about the type of land cover (forest, grassland, urban, etc.).

    Parameters:
    latitude	required	Latitude in WGS84
    longitude	required	Longitude in WGS84
    year	optional	WorldCover year (default: 2021, which is the latest available)
    scale	optional	Sampling scale in meters (default: 10m native resolution)

    Returns:
    str: Land cover class code at the point

    Land Cover Classes:
    10 - Tree cover
    20 - Shrubland
    30 - Grassland
    40 - Cropland
    50 - Built-up
    60 - Bare / sparse vegetation
    70 - Snow and ice
    80 - Permanent water bodies
    90 - Herbaceous wetland
    95 - Mangroves
    100 - Moss and lichen
    """
    init_earth_engine()

    result = get_worldcover_class(
        latitude=latitude,
        longitude=longitude,
        year=year,
        scale=scale,
    )

    if result is None:
        return "No WorldCover land cover data available for the specified location."

    # Map class codes to descriptions
    class_map = {
        10: "Tree cover",
        20: "Shrubland",
        30: "Grassland",
        40: "Cropland",
        50: "Built-up",
        60: "Bare / sparse vegetation",
        70: "Snow and ice",
        80: "Permanent water bodies",
        90: "Herbaceous wetland",
        95: "Mangroves",
        100: "Moss and lichen",
    }

    description = class_map.get(result, "Unknown")
    return f"WorldCover 2021 Land Cover Class: {result} - {description}"


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
