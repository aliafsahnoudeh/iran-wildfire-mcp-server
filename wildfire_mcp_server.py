from datetime import datetime

from mcp.server.fastmcp import FastMCP

from .src.agents import (
    AddressAgent,
    AirPollutionAgent,
    BoundingBox,
    FireFuelAgent,
    LikelyFireAgent,
    WeatherForecastAgent,
)

mcp = FastMCP("wildfire_mcp_server")


fire_agent = LikelyFireAgent()
fire_fuel_agent = FireFuelAgent()
address_agent = AddressAgent()
weather_agent = WeatherForecastAgent()
air_pollution_agent = AirPollutionAgent()


@mcp.tool()
async def get_potential_wildfires(
    date: str | None = None,
    frp: float = 1,
    bright_ti4: float = 50,
    in_iran: bool = False,
    bounding_box: BoundingBox | None = None,
) -> str:
    """
    Get potential wildfires in Iran for a specific date using NASA FIRMS data.
    This function is a starting point for further analysis of detected fires.

    Parameters:
        date (str): Date in YYYY-MM-DD format. If None, uses the current date.
        frp (float): Fire Radiative Power threshold.
        bright_ti4 (float): Brightness temperature threshold.
        in_iran: If True, only returns fires within Iran's borders. In case of passing it True, leave the bounding_box as None.
        bounding_box: Custom bounding box to limit the search area
    """
    response = fire_agent.fetch_likely_fires(
        start_date=date,
        end_date=date,
        frp=frp,
        bright_ti4=bright_ti4,
        in_iran=in_iran,
        bounding_box=bounding_box,
    )
    date = date or datetime.utcnow().strftime("%Y-%m-%d")
    output = [f"Fires detected by NASA FIRMS in Iran on {date}:\n\n"]
    for i, fire in enumerate(response, 1):
        output.append(f"Fire {i} Details:")
        output.append(fire.to_human_readable())
        output.append(10 * "-")

    return "\n".join(output)


@mcp.tool()
async def get_address(
    latitude: float,
    longitude: float,
) -> str:
    """
    Get the address for the given latitude and longitude.

    Parameters:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        str

    """
    response = address_agent.get_address(
        latitude=latitude,
        longitude=longitude,
    )
    return response.to_human_readable()  # type: ignore


@mcp.tool()
async def get_weather_forecast(
    latitude: float,
    longitude: float,
) -> str:
    """
    You can search weather forecast for 5 days with data every 3 hours by geographic coordinates.
    All weather data can be obtained in JSON and XML formats.

    Parameters:
        latitude	required	Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
        longitude	required	Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API

    Returns:
        str
    """
    response = weather_agent.get_forecast(
        latitude=latitude,
        longitude=longitude,
    )
    return response.to_human_readable()  # type: ignore


@mcp.tool()
async def get_current_air_pollution_data(
    latitude: float,
    longitude: float,
) -> str:
    """
    Fetch current air pollution data for the given latitude and longitude.

    Parameters:
        latitude	required	Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
        longitude	required	Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API

    Returns:
        str
    """
    response = air_pollution_agent.fetch_current_air_pollution(
        latitude=latitude,
        longitude=longitude,
    )
    return response.to_human_readable()  # type: ignore


@mcp.tool()
async def get_historical_air_pollution_data(
    latitude: float,
    longitude: float,
    start_date: str,  # YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    end_date: str,  # YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
) -> str:
    """
    Air Pollution API provides historical air pollution data for any coordinates on the globe.

    Parameters:
    latitude	required	Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
    longitude	required	Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API
    start_date	required	Start of the period (format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
    end_date	required	End of the period (format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)

    """
    response = air_pollution_agent.fetch_historical_air_pollution(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
    )
    return response.to_human_readable()  # type: ignore


@mcp.tool()
async def is_fire_fuel(
    latitude: float,
    longitude: float,
) -> bool:
    """
    Check if the given latitude and longitude are in a potential wildfire fuel area.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        bool: True if the location is in a potential wildfire fuel area, False otherwise.
    """
    return fire_fuel_agent.is_fire_fuel(latitude, longitude)


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
