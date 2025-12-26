import logging
import os
import sys
import time
from pathlib import Path

import pandas as pd
import plotly.express as px

# Must add path before other imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from src import (
    AddressAgent,
    AirPollutionAgent,
    FireFuelAgent,
    LikelyFireAgent,
    RawFireData,
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
    fire_fuel_agent = FireFuelAgent()
    address_agent = AddressAgent()
    weather_agent = WeatherForecastAgent()
    air_pollution_agent = AirPollutionAgent()

    try:
        logger.info(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}")

        # Fetch likely fires using the fire agent
        likely_fires = fire_agent.fetch_likely_fires(
            start_date="2025-11-18", end_date="2025-11-18", frp=1, bright_ti4=50
        )

        detected_fires: list[RawFireData] = []
        test_count = 0

        for fire in likely_fires:
            test_count += 1
            if test_count > 30:
                break

            lat = fire.latitude
            lon = fire.longitude

            try:
                # Check if location is is_fire_fuel using forest agent
                is_fire_fuel = fire_fuel_agent.is_fire_fuel(lat, lon)
                logger.info(
                    f"Checked is_fire_fuel area for fire at ({lat}, {lon}): {is_fire_fuel}"
                )
                # Add delay to avoid rate limiting by Overpass API
                time.sleep(3)
            except Exception as e:
                logger.error(
                    f"Error checking is_fire_fuel area for fire at ({lat}, {lon}): {e}"
                )
                continue

            if is_fire_fuel:
                detected_fires.append(fire)
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

        if len(detected_fires) > 0:
            # Convert fires to DataFrame for plotting
            fire_data = pd.DataFrame(
                [
                    {
                        "Latitude": fire.latitude,
                        "Longitude": fire.longitude,
                        "Brightness (K)": fire.bright_ti4,
                        "FRP (MW)": fire.frp,
                        "Date": fire.acq_date,
                        "Time": fire.acq_time,
                        "Satellite": fire.satellite,
                    }
                    for fire in detected_fires
                ]
            )

            # Create map centered on Iran
            fig = px.scatter_mapbox(
                fire_data,
                lat="Latitude",
                lon="Longitude",
                hover_name="Date",
                hover_data={
                    "Latitude": ":.4f",
                    "Longitude": ":.4f",
                    "Brightness (K)": ":.1f",
                    "FRP (MW)": ":.2f",
                    "Time": True,
                    "Satellite": True,
                },
                color="FRP (MW)",
                size="Brightness (K)",
                color_continuous_scale="hot",
                size_max=15,
                zoom=5,
                mapbox_style="open-street-map",
                title=f"({len(detected_fires)} fires)",
                height=700,
            )

            # Save map as HTML
            map_filename = f"output/nasa_firms_fires_map_{timestamp}.html"
            fig.write_html(map_filename)
            print(f"Map saved to {map_filename}")

            # Show the map
            fig.show()
    except Exception as e:
        logger.error(f"Error in main functionality test: {e}")
    finally:
        logger.info(f"Finished at: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}")
        logger.info(f"Duration: {time.perf_counter():.2f} seconds")


if __name__ == "__main__":
    main()
