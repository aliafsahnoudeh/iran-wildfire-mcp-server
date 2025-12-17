import logging
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domains.nasa_firms import get_fires_in_iran
from src.domains.open_weather_map import (
    get_current_air_pollution_data,
    get_openweather_onecall,
    get_reverse_geocoding,
)
from src.domains.overpass import is_forest

load_dotenv()

logger = logging.getLogger(__name__)
FIRE_DEV_MODE = os.getenv("FIRE_DEV_MODE")
if FIRE_DEV_MODE == "1":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.WARNING)


def main():
    try:
        likely_fires = get_fires_in_iran(
            start_date="2025-11-19", end_date="2025-11-19", frp=1, bright_ti4=50
        )

        for fire in likely_fires:
            lat = fire.latitude
            lon = fire.longitude

            try:
                # Check if location is forested (caching handled automatically)
                forested = is_forest(lat, lon)
                logger.info(
                    f"Checked forested area for fire at ({lat}, {lon}): {forested}"
                )
                # Add delay to avoid rate limiting by Overpass API
                time.sleep(3)
            except Exception as e:
                logger.error(
                    f"Error checking forested area for fire at ({lat}, {lon}): {e}"
                )
                continue

            if forested:
                output = [f"Fire ({lat}, {lon}):\n"]
                address = get_reverse_geocoding(
                    latitude=fire.latitude,
                    longitude=fire.longitude,
                )
                output.append(address.to_human_readable())
                openweather_result = get_openweather_onecall(
                    latitude=fire.latitude,
                    longitude=fire.longitude,
                )
                output.append(openweather_result.to_human_readable())
                current_air_pollution = get_current_air_pollution_data(
                    latitude=fire.latitude,
                    longitude=fire.longitude,
                )
                output.append(current_air_pollution.to_human_readable())
                # save to a text file with date and time in filename
                timestamp = fire.acq_date + "_" + str(fire.acq_time)
                output_filename = f"output/fire_{lat}_{lon}_{timestamp}.txt"
                with open(output_filename, "w") as f:
                    f.write("\n\n".join(output))
    except Exception as e:
        logger.error(f"Error in main functionality test: {e}")


if __name__ == "__main__":
    main()
