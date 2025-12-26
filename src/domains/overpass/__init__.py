"""Overpass API domain for forest checking with caching."""

from .core import get_cache_stats, is_fire_fuel, refresh_cache

__all__ = ["is_fire_fuel", "refresh_cache", "get_cache_stats"]
