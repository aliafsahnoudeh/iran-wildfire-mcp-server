"""Utility script to refresh the Overpass API cache.

This script can be run manually to update all cache entries with fresh data.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domains.overpass import get_cache_stats, refresh_cache

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Refresh Overpass API forest check cache"
    )
    parser.add_argument(
        "--search-radius",
        type=int,
        default=1500,
        help="Search radius in meters for forest features (default: 1500)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Delay in seconds between API calls (default: 3.0)",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only show cache statistics without refreshing",
    )

    args = parser.parse_args()

    # Show current cache stats
    logger.info("=" * 60)
    logger.info("Current Cache Statistics")
    logger.info("=" * 60)
    stats = get_cache_stats()
    logger.info(f"Total entries: {stats['total_entries']}")
    logger.info(f"Forest locations: {stats['forest_count']}")
    logger.info(f"Non-forest locations: {stats['non_forest_count']}")
    logger.info(f"Average age: {stats['average_age_days']:.2f} days")
    logger.info("=" * 60)

    if args.stats_only:
        return

    # Perform cache refresh
    logger.info("\nStarting cache refresh (all entries will be updated)...")
    logger.info(f"Search radius: {args.search_radius}m")
    logger.info(f"Delay between calls: {args.delay}s")
    logger.info("=" * 60)

    try:
        result = refresh_cache(
            search_radius=args.search_radius,
            delay_seconds=args.delay,
        )

        logger.info("=" * 60)
        logger.info("Cache Refresh Complete")
        logger.info("=" * 60)
        logger.info(f"Total entries: {result['total']}")
        logger.info(f"Updated: {result['updated']}")
        logger.info(f"Failed: {result['failed']}")
        logger.info("=" * 60)

        # Show updated stats
        logger.info("\nUpdated Cache Statistics")
        logger.info("=" * 60)
        new_stats = get_cache_stats()
        logger.info(f"Total entries: {new_stats['total_entries']}")
        logger.info(f"Forest locations: {new_stats['forest_count']}")
        logger.info(f"Non-forest locations: {new_stats['non_forest_count']}")
        logger.info(f"Average age: {new_stats['average_age_days']:.2f} days")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error during cache refresh: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
