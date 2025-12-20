from src.domains.open_weather_map import (
    ForecastResponse,
    get_openweather_onecall,
)


class WeatherForecastAgent:
    def get_forecast(self, latitude: float, longitude: float) -> ForecastResponse:
        """
        Get weather forecast for the given latitude and longitude.

        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.

        Returns:
            ForecastResponse: Weather forecast data.
        """
        return get_openweather_onecall(latitude=latitude, longitude=longitude)
