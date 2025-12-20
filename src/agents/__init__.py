"""
Agents module for Iran Wildfire MCP Server.

This module provides high-level agent classes that encapsulate domain-specific
functionality for wildfire detection, monitoring, and analysis.
"""

from .address_agent import AddressAgent
from .air_pollution_agent import AirPollutionAgent
from .fire_fuel_agent import FireFuelAgent
from .likely_fire_agent import LikelyFireAgent
from .weather_forecast_agent import WeatherForecastAgent

__all__ = [
    "AddressAgent",
    "AirPollutionAgent",
    "FireFuelAgent",
    "LikelyFireAgent",
    "WeatherForecastAgent",
]
