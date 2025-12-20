from src.domains.open_weather_map import (
    AirPollutionResponse,
    get_current_air_pollution_data,
    get_historical_air_pollution_data,
)


class AirPollutionAgent:
    def fetch_current_air_pollution(
        self, latitude: float, longitude: float
    ) -> AirPollutionResponse:
        """
        Fetch current air pollution data for the given latitude and longitude.
        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
        Returns:
            AirPollutionResponse: Current air pollution data.
        """
        return get_current_air_pollution_data(latitude=latitude, longitude=longitude)

    def fetch_historical_air_pollution(
        self,
        latitude: float,
        longitude: float,
        start: int,
        end: int,
    ) -> AirPollutionResponse:
        """
        Fetch historical air pollution data for the given latitude and longitude
        between the specified start and end timestamps.
        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
            start (int): Start timestamp (Unix time).
            end (int): End timestamp (Unix time).
        Returns:
            AirPollutionResponse: Historical air pollution data.
        """
        return get_historical_air_pollution_data(
            latitude=latitude, longitude=longitude, start=start, end=end
        )
