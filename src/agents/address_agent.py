from src.domains.open_weather_map import ReverseGeocodingResponse, get_reverse_geocoding


class AddressAgent:
    def __init__(self):
        pass

    def get_address(
        self, latitude: float, longitude: float
    ) -> ReverseGeocodingResponse:
        """Get the address for the given latitude and longitude.

        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
        Returns:
            ReverseGeocodingResponse: Address information.
        """
        return get_reverse_geocoding(
            latitude=latitude,
            longitude=longitude,
        )
