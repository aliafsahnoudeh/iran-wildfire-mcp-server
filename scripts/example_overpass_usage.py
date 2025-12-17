"""Example: Using the Overpass caching system for fire analysis."""

import logging
import sys
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domains.overpass import get_cache_stats, is_forest

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example 1: Basic forest checking."""
    logger.info("=" * 60)
    logger.info("Example 1: Basic Forest Checking")
    logger.info("=" * 60)

    # Tehran coordinates
    lat, lon = 35.6892, 51.3890

    logger.info(f"Checking if Tehran ({lat}, {lon}) is forested...")
    is_forest_result = is_forest(lat, lon)
    logger.info(f"Result: {'Forested' if is_forest_result else 'Not forested'}\n")


def example_custom_config():
    """Example 2: Using custom search radius."""
    logger.info("=" * 60)
    logger.info("Example 2: Custom Search Radius")
    logger.info("=" * 60)

    # Zagros Mountains (likely forested)
    lat, lon = 33.5, 51.5

    logger.info("Using fine-grained grid (0.001°) and 2000m search radius")
    is_forest_result = is_forest(
        lat=lat,
        lon=lon,
        grid_precision=0.001,  # ~111m cells (default)
        search_radius=2000,  # Extra-large 2km search radius
    )
    logger.info(f"Result: {'Forested' if is_forest_result else 'Not forested'}\n")


def example_batch_checking():
    """Example 3: Checking multiple locations efficiently."""
    logger.info("=" * 60)
    logger.info("Example 3: Batch Checking Multiple Locations")
    logger.info("=" * 60)

    # Simulated fire locations
    fire_locations = [
        (35.7, 51.4, "Tehran area"),
        (36.8, 54.5, "Golestan forest"),
        (32.6, 51.7, "Isfahan area"),
        (35.5, 51.3, "Alborz mountains"),
    ]

    logger.info(f"Checking {len(fire_locations)} locations...\n")

    forested_fires = []
    for lat, lon, name in fire_locations:
        try:
            is_forest_result = is_forest(lat, lon)
            logger.info(
                f"  {name} ({lat}, {lon}): "
                f"{'Forested' if is_forest_result else 'Not forested'}"
            )

            if is_forest_result:
                forested_fires.append((lat, lon, name))

            # Rate limiting: wait between checks
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"  Error checking {name}: {e}")
            continue

    logger.info(f"\nFound {len(forested_fires)} forested fire locations:")
    for lat, lon, name in forested_fires:
        logger.info(f"  - {name} at ({lat}, {lon})")
    logger.info("")


def example_cache_statistics():
    """Example 4: Viewing cache statistics."""
    logger.info("=" * 60)
    logger.info("Example 4: Cache Statistics")
    logger.info("=" * 60)

    stats = get_cache_stats()

    logger.info("Current Cache Status:")
    logger.info(f"  Total cached locations: {stats['total_entries']}")
    logger.info(f"  Forested locations: {stats['forest_count']}")
    logger.info(f"  Non-forested locations: {stats['non_forest_count']}")
    logger.info(f"  Average cache age: {stats['average_age_days']:.2f} days")

    if stats["total_entries"] > 0:
        hit_rate = (stats["forest_count"] / stats["total_entries"]) * 100
        logger.info(f"  Forest percentage: {hit_rate:.1f}%")

    logger.info("")


def example_with_error_handling():
    """Example 5: Proper error handling."""
    logger.info("=" * 60)
    logger.info("Example 5: Error Handling")
    logger.info("=" * 60)

    # Locations to check
    locations = [
        (35.0, 51.0),
        (36.0, 52.0),
        (37.0, 53.0),
    ]

    results = {}
    failures = []

    for lat, lon in locations:
        try:
            is_forest_result = is_forest(lat, lon)
            results[(lat, lon)] = is_forest_result
            logger.info(
                f"  ({lat}, {lon}): "
                f"{'Forested' if is_forest_result else 'Not forested'}"
            )
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"  ({lat}, {lon}): Failed - {e}")
            failures.append((lat, lon))
            continue

    logger.info(f"\nSuccessfully checked: {len(results)}/{len(locations)} locations")
    if failures:
        logger.info(f"Failed to check: {len(failures)} locations")
    logger.info("")


def main():
    """Run all examples."""
    logger.info("\n" + "=" * 60)
    logger.info("Overpass Cache System - Usage Examples")
    logger.info("=" * 60 + "\n")

    # Show initial cache stats
    example_cache_statistics()

    # Run examples
    example_basic_usage()
    example_custom_config()
    example_batch_checking()
    example_with_error_handling()

    # Show final cache stats
    example_cache_statistics()

    logger.info("=" * 60)
    logger.info("Examples completed!")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("  1. Check cache file: cat output/overpass_cache.json")
    logger.info(
        "  2. View statistics: python scripts/refresh_overpass_cache.py --stats-only"
    )
    logger.info("  3. Refresh cache: python scripts/refresh_overpass_cache.py")
    logger.info("")


if __name__ == "__main__":
    main()
