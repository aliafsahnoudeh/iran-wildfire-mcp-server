"""
Agents module for Wildfire MCP Server.

This module provides high-level agent classes that encapsulate domain-specific
functionality for wildfire detection, monitoring, and analysis.
"""

# Re-export domain types for convenience
from ..domains.nasa_firms import BoundingBox, Confidence, DayNight, RawFireData
from ..domains.open_weather_map import (
    AirPollutionComponents,
    AirPollutionItem,
    AirPollutionResponse,
    AirQualityMain,
    ForecastItem,
    ForecastResponse,
    ReverseGeocodingLocation,
    ReverseGeocodingResponse,
)
from .address_agent import AddressAgent
from .air_pollution_agent import AirPollutionAgent
from .fire_fuel_agent import FireFuelAgent
from .likely_fire_agent import LikelyFireAgent
from .weather_forecast_agent import WeatherForecastAgent

__all__ = [
    # Agents
    "AddressAgent",
    "AirPollutionAgent",
    "FireFuelAgent",
    "LikelyFireAgent",
    "WeatherForecastAgent",
    # NASA FIRMS types
    "BoundingBox",
    "Confidence",
    "DayNight",
    "RawFireData",
    # Open Weather Map types
    "AirPollutionComponents",
    "AirPollutionItem",
    "AirPollutionResponse",
    "AirQualityMain",
    "ForecastItem",
    "ForecastResponse",
    "ReverseGeocodingLocation",
    "ReverseGeocodingResponse",
]
