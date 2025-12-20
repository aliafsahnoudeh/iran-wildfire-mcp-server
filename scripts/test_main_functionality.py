import logging
import os
import sys
import time
from pathlib import Path

# Must add path before other imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from src import (
    AddressAgent,
    AirPollutionAgent,
    ForestAgent,
    LikelyFireAgent,
    WeatherForecastAgent,
)

load_dotenv()

logger = logging.getLogger(__name__)
FIRE_DEV_MODE = os.getenv("FIRE_DEV_MODE")
if FIRE_DEV_MODE == "1":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.WARNING)


def main():
    # Initialize agents
    fire_agent = LikelyFireAgent()
    forest_agent = ForestAgent()
    address_agent = AddressAgent()
    weather_agent = WeatherForecastAgent()
    air_pollution_agent = AirPollutionAgent()

    try:
        logger.info(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}")

        # Fetch likely fires using the fire agent
        likely_fires = fire_agent.fetch_likely_fires(
            start_date="2025-11-19", end_date="2025-11-19", frp=1, bright_ti4=50
        )

        for fire in likely_fires:
            lat = fire.latitude
            lon = fire.longitude

            try:
                # Check if location is forested using forest agent
                forested = forest_agent.is_forest(lat, lon)
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
                output = [f"Fire ({lat}, {lon}):\\n"]

                # Get address using address agent
                address = address_agent.get_address(
                    latitude=fire.latitude,
                    longitude=fire.longitude,
                )
                output.append(address.to_human_readable())

                # Get weather forecast using weather agent
                weather_forecast = weather_agent.get_forecast(
                    latitude=fire.latitude,
                    longitude=fire.longitude,
                )
                output.append(weather_forecast.to_human_readable())

                # Get current air pollution using air pollution agent
                current_air_pollution = air_pollution_agent.fetch_current_air_pollution(
                    latitude=fire.latitude,
                    longitude=fire.longitude,
                )
                output.append(current_air_pollution.to_human_readable())

                # Save to a text file with date and time in filename
                timestamp = fire.acq_date + "_" + str(fire.acq_time)
                output_filename = f"output/fire_{lat}_{lon}_{timestamp}.txt"
                with open(output_filename, "w") as f:
                    f.write("\\n\\n".join(output))
    except Exception as e:
        logger.error(f"Error in main functionality test: {e}")
    finally:
        logger.info(f"Finished at: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}")
        logger.info(f"Duration: {time.perf_counter():.2f} seconds")


if __name__ == "__main__":
    main()
