"""
Iran Wildfire MCP Server - Main Package Interface.

This package provides a comprehensive set of tools for detecting, monitoring,
and analyzing wildfires in Iran using multiple data sources and APIs.

Main Components:
- Agents: High-level classes for specific tasks (fire detection, weather, pollution, etc.)
- Types: Data models for API responses and domain entities

Usage Example:
    from src import LikelyFireAgent, FireFuelAgent, WeatherForecastAgent
    from src.types import RawFireData, ForecastResponse

    # Initialize agents
    fire_agent = LikelyFireAgent(satellite_id="VIIRS")
    fire_fuel_agent = FireFuelAgent()
    weather_agent = WeatherForecastAgent()

    # Use agents
    fires = fire_agent.fetch_likely_fires(start_date="2025-01-01", end_date="2025-01-02")
    for fire in fires:
        if fire_fuel_agent.is_fire_fuel(fire.latitude, fire.longitude):
            forecast = weather_agent.get_forecast(fire.latitude, fire.longitude)
"""

# Export all agents
# Make types available as a submodule
from . import types
from .agents import (
    AddressAgent,
    AirPollutionAgent,
    FireFuelAgent,
    LikelyFireAgent,
    WeatherForecastAgent,
)

# Export commonly used types from domains
from .domains.nasa_firms import Confidence, DayNight, RawFireData
from .domains.open_weather_map import (
    AirPollutionComponents,
    AirPollutionItem,
    AirPollutionResponse,
    AirQualityMain,
    ForecastItem,
    ForecastResponse,
    ReverseGeocodingLocation,
    ReverseGeocodingResponse,
)

__all__ = [
    # Agents
    "AddressAgent",
    "AirPollutionAgent",
    "FireFuelAgent",
    "LikelyFireAgent",
    "WeatherForecastAgent",
    # NASA FIRMS Types
    "RawFireData",
    "Confidence",
    "DayNight",
    # OpenWeatherMap Types
    "AirPollutionResponse",
    "AirQualityMain",
    "AirPollutionComponents",
    "AirPollutionItem",
    "ForecastResponse",
    "ForecastItem",
    "ReverseGeocodingResponse",
    "ReverseGeocodingLocation",
    # Types submodule
    "types",
]
