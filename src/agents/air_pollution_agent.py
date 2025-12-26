from datetime import datetime

from src.domains.open_weather_map import (
    AirPollutionResponse,
    get_current_air_pollution_data,
    get_historical_air_pollution_data,
)


class AirPollutionAgent:
    def fetch_current_air_pollution(
        self,
        latitude: float,
        longitude: float,
        api_key: str | None = None,
        timeout: int = 30,
    ) -> AirPollutionResponse:
        """
        Fetch current air pollution data for the given latitude and longitude.
        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
        Returns:
            AirPollutionResponse: Current air pollution data.
        """
        return get_current_air_pollution_data(
            latitude=latitude, longitude=longitude, api_key=api_key, timeout=timeout
        )

    def fetch_historical_air_pollution(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        api_key: str | None = None,
        timeout: int = 30,
    ) -> AirPollutionResponse:
        """
        Fetch historical air pollution data for the given latitude and longitude
        between the specified start and end dates.
        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
            start_date (str): Start date (format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS).
            end_date (str): End date (format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS).
        Returns:
            AirPollutionResponse: Historical air pollution data.
        """
        # Convert date strings to Unix timestamps
        try:
            # Try parsing with time first
            start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Fall back to date only (assume start of day)
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        try:
            # Try parsing with time first
            end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Fall back to date only (assume end of day)
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)

        start_timestamp = int(start_dt.timestamp())
        end_timestamp = int(end_dt.timestamp())

        return get_historical_air_pollution_data(
            latitude=latitude,
            longitude=longitude,
            start=start_timestamp,
            end=end_timestamp,
            api_key=api_key,
            timeout=timeout,
        )
