from src.domains.open_weather_map import (
    ForecastResponse,
    get_openweather_onecall,
)


class WeatherForecastAgent:
    def get_forecast(
        self,
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
            timeout	optional	Request timeout in seconds (default is 30 seconds)

        Returns:
            ForecastResponse
        """
        return get_openweather_onecall(
            latitude=latitude, longitude=longitude, api_key=api_key, timeout=timeout
        )
