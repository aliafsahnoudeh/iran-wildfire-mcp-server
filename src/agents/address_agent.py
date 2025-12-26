from src.domains.open_weather_map import ReverseGeocodingResponse, get_reverse_geocoding


class AddressAgent:
    def __init__(self):
        pass

    def get_address(
        self,
        latitude: float,
        longitude: float,
        api_key: str | None = None,
        limit: int = 1,
        timeout: int = 30,
    ) -> ReverseGeocodingResponse:
        """Get the address for the given latitude and longitude.

        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
            limit	optional	Number of the location names in the API response (several results can be returned in the API response)
            timeout	optional	Request timeout in seconds (default is 30 seconds)

        Returns:
            ReverseGeocodingResponse
        """
        return get_reverse_geocoding(
            latitude=latitude,
            longitude=longitude,
            api_key=api_key,
            limit=limit,
            timeout=timeout,
        )
