"""Simple test to verify the Overpass caching system works."""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domains.overpass import get_cache_stats, is_forest

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_cache_system():
    """Test the caching system with a known location."""

    # Test coordinates (Tehran area)
    test_lat = 35.6892
    test_lon = 51.3890

    logger.info("=" * 60)
    logger.info("Testing Overpass Cache System")
    logger.info("=" * 60)

    # Show initial cache stats
    logger.info("\nInitial Cache Statistics:")
    stats = get_cache_stats()
    logger.info(f"Total entries: {stats['total_entries']}")
    logger.info(f"Forest locations: {stats['forest_count']}")
    logger.info(f"Non-forest locations: {stats['non_forest_count']}")
    logger.info(f"Average age: {stats['average_age_days']:.2f} days")

    # Test forest check
    logger.info(f"\nChecking if ({test_lat}, {test_lon}) is forested...")
    try:
        is_forest_result = is_forest(test_lat, test_lon)
        logger.info(f"Result: {'Forested' if is_forest_result else 'Not forested'}")
    except Exception as e:
        logger.error(f"Error during forest check: {e}")
        return False

    # Show updated cache stats
    logger.info("\nUpdated Cache Statistics:")
    stats = get_cache_stats()
    logger.info(f"Total entries: {stats['total_entries']}")
    logger.info(f"Forest locations: {stats['forest_count']}")
    logger.info(f"Non-forest locations: {stats['non_forest_count']}")
    logger.info(f"Average age: {stats['average_age_days']:.2f} days")

    # Test cache hit (should be instant)
    logger.info("\nTesting cache hit for same location...")
    try:
        is_forest_2 = is_forest(test_lat, test_lon)
        logger.info(
            f"Result: {'Forested' if is_forest_2 else 'Not forested'} (from cache)"
        )
        if is_forest_result != is_forest_2:
            logger.error("Cache returned different result!")
            return False
    except Exception as e:
        logger.error(f"Error during cached forest check: {e}")
        return False

    logger.info("\n" + "=" * 60)
    logger.info("Cache system test completed successfully!")
    logger.info("=" * 60)
    return True


if __name__ == "__main__":
    success = test_cache_system()
    sys.exit(0 if success else 1)
