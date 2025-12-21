import argparse
import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domains.overpass import is_fire_fuel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run all examples."""
    parser = argparse.ArgumentParser(
        description="Check if a location is forested using Overpass API"
    )
    parser.add_argument(
        "--lat",
        type=float,
        default=35.6892,
        help="Latitude (default: 35.6892 - Tehran)",
    )
    parser.add_argument(
        "--lon",
        type=float,
        default=51.3890,
        help="Longitude (default: 51.3890 - Tehran)",
    )
    args = parser.parse_args()
    logger.info(f"Checking location ({args.lat}, {args.lon}) for forest coverage...")
    is_forest_result = is_fire_fuel(args.lat, args.lon, search_radius=1500)
    logger.info(f"Result: {'Forested' if is_forest_result else 'Not forested'}\n")


if __name__ == "__main__":
    main()
