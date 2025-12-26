"""Core functionality for Overpass API forest checking with caching."""

import json
import logging
import time
from datetime import datetime
from pathlib import Path

import requests

from .types import CacheConfig, CacheEntry

logger = logging.getLogger(__name__)

# Cache file location
CACHE_DIR = Path("output")
CACHE_FILE = CACHE_DIR / "overpass_cache.json"

# Module-level cache - loaded once on import
_CACHE: dict[str, CacheEntry] = {}


def _ensure_cache_dir() -> None:
    """Ensure the cache directory exists."""
    CACHE_DIR.mkdir(exist_ok=True)


def _load_cache_from_disk() -> dict[str, CacheEntry]:
    """Load cache from JSON file.

    Returns:
        Dictionary mapping cache keys to CacheEntry objects
    """
    if not CACHE_FILE.exists():
        return {}

    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
        return {key: CacheEntry.from_dict(entry) for key, entry in data.items()}
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Failed to load cache file: {e}. Starting with empty cache.")
        return {}


def _initialize_cache() -> None:
    """Initialize the module-level cache on first import."""
    global _CACHE
    if not _CACHE:  # Only load if not already loaded
        _CACHE = _load_cache_from_disk()
        logger.debug(f"Loaded {len(_CACHE)} entries from cache file")


def _save_cache_to_disk() -> None:
    """Save the module-level cache to JSON file."""
    _ensure_cache_dir()
    data = {key: entry.to_dict() for key, entry in _CACHE.items()}
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _query_overpass_api(
    lat: float,
    lon: float,
    search_radius: int,
    timeout: int = 30,
    max_retries: int = 5,
) -> tuple[bool, int]:
    """Query Overpass API to check if location is forested.

    Args:
        lat: Latitude
        lon: Longitude
        search_radius: Search radius in meters
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts

    Returns:
        Tuple of (is_fire_fuel, element_count)

    Raises:
        Exception: If API call fails after all retries
    """
    # Fuel features (vegetation that can carry fire)
    fuel_query = f"""
      nwr(around:{search_radius},{lat},{lon})["natural"="wood"];
      nwr(around:{search_radius},{lat},{lon})["landuse"="forest"];
      nwr(around:{search_radius},{lat},{lon})["natural"="scrub"];
      nwr(around:{search_radius},{lat},{lon})["natural"="grassland"];
      nwr(around:{search_radius},{lat},{lon})["landcover"="trees"];
      nwr(around:{search_radius},{lat},{lon})["landcover"="grass"];
    """

    # Clear non-fuel / misleading features (water, bare ground, dense built-up)
    exclude_query = f"""
      nwr(around:{search_radius},{lat},{lon})["natural"="water"];
      nwr(around:{search_radius},{lat},{lon})["waterway"];
      nwr(around:{search_radius},{lat},{lon})["natural"="bare_rock"];
      nwr(around:{search_radius},{lat},{lon})["natural"="sand"];
      nwr(around:{search_radius},{lat},{lon})["landuse"~"^(residential|commercial|industrial|construction|quarry)$"];
      nwr(around:{search_radius},{lat},{lon})["building"];
      nwr(around:{search_radius},{lat},{lon})["highway"];
    """

    query = f"""
    [out:json][timeout:25];
    (
      {fuel_query}
      {exclude_query}
    );
    out tags qt;
    """

    url = "https://overpass-api.de/api/interpreter"
    headers = {"User-Agent": "Wildfire-MCP-Server/1.0"}

    for attempt in range(max_retries):
        try:
            logger.info(
                "Querying Overpass API for lat=%s lon=%s radius_m=%s (attempt %s/%s)",
                lat,
                lon,
                search_radius,
                attempt + 1,
                max_retries,
            )
            r = requests.post(
                url, data={"data": query}, headers=headers, timeout=timeout
            )
            r.raise_for_status()
            data = r.json()
            logger.info("Overpass API raw response: %s", data)
            elements = data.get("elements", [])

            # --- scoring ---
            fuel_score = 0
            exclude_score = 0

            fuel_hits = {
                "wood": 0,
                "forest": 0,
                "scrub": 0,
                "grassland": 0,
                "trees": 0,
                "grass": 0,
            }
            exclude_hits = {"water": 0, "bare": 0, "built": 0, "roads": 0}

            for el in elements:
                tags = el.get("tags", {})
                natural = tags.get("natural")
                landuse = tags.get("landuse")
                landcover = tags.get("landcover")

                # --- fuel ---
                if natural == "wood":
                    fuel_score += 4
                    fuel_hits["wood"] += 1
                elif landuse == "forest":
                    fuel_score += 4
                    fuel_hits["forest"] += 1
                elif natural == "scrub":
                    fuel_score += 3
                    fuel_hits["scrub"] += 1
                elif natural == "grassland":
                    fuel_score += 2
                    fuel_hits["grassland"] += 1
                elif landcover == "trees":
                    fuel_score += 3
                    fuel_hits["trees"] += 1
                elif landcover == "grass":
                    fuel_score += 1
                    fuel_hits["grass"] += 1

                # --- exclusions ---
                if natural == "water" or "waterway" in tags:
                    exclude_score += 6
                    exclude_hits["water"] += 1
                if natural in ("bare_rock", "sand"):
                    exclude_score += 4
                    exclude_hits["bare"] += 1
                if "building" in tags or landuse in (
                    "residential",
                    "commercial",
                    "industrial",
                    "construction",
                    "quarry",
                ):
                    exclude_score += 3
                    exclude_hits["built"] += 1
                if "highway" in tags:
                    exclude_score += 1
                    exclude_hits["roads"] += 1

            # Decision:
            # - require some fuel signal
            # - if exclusions dominate, return False
            wildfire_fuel_likely = (fuel_score >= 4) and (
                exclude_score <= fuel_score + 2
            )

            debug = {
                "fuel_score": fuel_score,
                "exclude_score": exclude_score,
                "fuel_hits": fuel_hits,
                "exclude_hits": exclude_hits,
                "elements": len(elements),
                "radius_m": search_radius,
            }
            logger.debug("Overpass scoring debug: %s", debug)
            return wildfire_fuel_likely, len(elements)

        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
            else:
                raise


def is_fire_fuel(
    lat: float,
    lon: float,
    grid_precision: float = 0.001,
    search_radius: int = 1500,
    use_cache: bool = False,
) -> bool:
    """Check if a location is fire fuel.

    Conservative caching strategy optimized for wildfire detection accuracy:
    - Fine grid precision (0.001° ≈ 111m) minimizes quantization errors
    - Large search radius (1500m) ensures forest detection even with quantization
    - Cache never expires - use refresh_cache() to manually update stale entries

    This prioritizes accuracy over performance to avoid missing forest fires.

    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        grid_precision: Grid cell size in degrees (default 0.001° ≈ 111m, conservative)
        search_radius: Radius in meters to search for forest features (default 1500m)

    Returns:
        True if the location is forested, False otherwise

    Raises:
        Exception: If Overpass API query fails after all retries
    """

    if use_cache:
        logger.warning("Using cache.")
        # Initialize cache on first call
        _initialize_cache()

        config = CacheConfig(
            grid_precision=grid_precision,
            search_radius=search_radius,
        )

        # Generate cache key
        cache_key = config.get_cache_key(lat, lon)

        # Check if we have a cache entry
        if cache_key in _CACHE:
            entry = _CACHE[cache_key]
            logger.info(
                f"Cache HIT for ({lat}, {lon}) -> grid ({entry.grid_lat}, {entry.grid_lon}): "
                f"is_fire_fuel={entry.is_fire_fuel}"
            )
            return entry.is_fire_fuel
        else:
            logger.info(f"No cache for ({lat}, {lon})")

    # Query Overpass API
    is_forest_result, element_count = _query_overpass_api(lat, lon, search_radius)

    if use_cache:
        # Update cache in memory
        grid_lat = config.quantize_coordinate(lat)
        grid_lon = config.quantize_coordinate(lon)
        entry = CacheEntry(
            grid_lat=grid_lat,
            grid_lon=grid_lon,
            is_fire_fuel=is_fire_fuel_result,
            last_checked=datetime.now().isoformat(),
            search_radius=search_radius,
            element_count=element_count,
        )
        _CACHE[cache_key] = entry

        # Save to disk
        _save_cache_to_disk()

        logger.info(
            f"Updated cache for ({lat}, {lon}) -> grid ({grid_lat}, {grid_lon}): "
            f"is_fire_fuel={is_fire_fuel_result}"
        )

    return is_fire_fuel_result


def refresh_cache(
    search_radius: int = 1500,
    delay_seconds: float = 3.0,
) -> dict[str, int]:
    """Refresh all cache entries by re-querying the Overpass API.

    This is a manual operation to update cached forest data. Call this periodically
    to keep cache data fresh, or when you suspect forest boundaries have changed.

    Args:
        search_radius: Radius in meters to search for forest features (default 1500m)
        delay_seconds: Delay between API calls to respect rate limits (default 3.0)

    Returns:
        Dictionary with statistics: {'total': int, 'updated': int, 'failed': int}
    """
    # Initialize cache
    _initialize_cache()

    stats = {"total": len(_CACHE), "updated": 0, "failed": 0}

    logger.info(f"Starting cache refresh. Total entries: {stats['total']}")

    for cache_key, entry in list(_CACHE.items()):
        logger.info(
            f"Refreshing cache entry for grid ({entry.grid_lat}, {entry.grid_lon})"
        )

        try:
            # Query Overpass API
            is_fire_fuel, element_count = _query_overpass_api(
                entry.grid_lat,
                entry.grid_lon,
                search_radius,
            )

            # Update cache entry in memory
            _CACHE[cache_key] = CacheEntry(
                grid_lat=entry.grid_lat,
                grid_lon=entry.grid_lon,
                is_fire_fuel=is_fire_fuel,
                last_checked=datetime.now().isoformat(),
                search_radius=search_radius,
                element_count=element_count,
            )

            stats["updated"] += 1
            logger.info(
                f"Updated cache entry for grid ({entry.grid_lat}, {entry.grid_lon}): "
                f"is_fire_fuel={is_fire_fuel}"
            )

            # Delay to respect rate limits
            time.sleep(delay_seconds)

        except Exception as e:
            stats["failed"] += 1
            logger.error(
                f"Failed to refresh cache entry for grid ({entry.grid_lat}, {entry.grid_lon}): {e}"
            )
            # Continue with other entries even if one fails
            continue

    # Save updated cache to disk
    _save_cache_to_disk()

    logger.info(
        f"Cache refresh completed. Updated: {stats['updated']}, Failed: {stats['failed']}"
    )

    return stats


def get_cache_stats() -> dict[str, int | float]:
    """Get statistics about the current cache.

    Returns:
        Dictionary with cache statistics including total entries,
        forest/non-forest counts, and average age
    """
    # Initialize cache
    _initialize_cache()

    if not _CACHE:
        return {
            "total_entries": 0,
            "forest_count": 0,
            "non_forest_count": 0,
            "average_age_days": 0.0,
        }

    forest_count = sum(1 for entry in _CACHE.values() if entry.is_fire_fuel)

    # Calculate average age
    now = datetime.now()
    total_age_days = 0.0
    for entry in _CACHE.values():
        checked_time = datetime.fromisoformat(entry.last_checked)
        age_days = (now - checked_time).total_seconds() / 86400
        total_age_days += age_days

    average_age_days = total_age_days / len(_CACHE) if _CACHE else 0.0

    return {
        "total_entries": len(_CACHE),
        "forest_count": forest_count,
        "non_forest_count": len(_CACHE) - forest_count,
        "average_age_days": round(average_age_days, 2),
    }


# Initialize cache on module import
_initialize_cache()
