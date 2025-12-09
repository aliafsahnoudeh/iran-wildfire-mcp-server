from typing import Optional

from mcp.server.fastmcp import FastMCP

from src.domains.open_weather_map.core import get_reverse_geocoding

mcp = FastMCP("iran_wildfire")


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


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
