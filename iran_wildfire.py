from datetime import datetime, timedelta
from typing import Optional

from mcp.server.fastmcp import FastMCP

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
        current_air_pollution = get_current_air_pollution_data(
            latitude=fire.latitude,
            longitude=fire.longitude,
        )
        output.append(20 * "-" + "")
        output.append("Current Air Pollution Data:\n")
        output.append(current_air_pollution.to_human_readable())  # type: ignore
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


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
