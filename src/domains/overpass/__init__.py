"""Overpass API domain for forest checking with caching."""

from .core import get_cache_stats, is_forest, refresh_cache

__all__ = ["is_forest", "refresh_cache", "get_cache_stats"]
