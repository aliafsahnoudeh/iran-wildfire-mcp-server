import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domains.nasa_firms import get_fires_in_iran

load_dotenv()

logger = logging.getLogger(__name__)
FIRE_DEV_MODE = os.getenv("FIRE_DEV_MODE")
if FIRE_DEV_MODE == "1":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.WARNING)


likely_fires = get_fires_in_iran(
    start_date="2025-11-19", end_date="2025-11-19", frp=1, bright_ti4=50
)

# Create filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"output/nasa_firms_fires_{timestamp}.txt"

# save the results to a text file as a table and put it in /output directory
with open(output_filename, "w") as f:
    f.write("Fires in Iran:\n")
    f.write("Latitude\tLongitude\tBrightness (TI4)\tFRP (MW)\tDate\tTime\n")
    for fire in likely_fires:
        f.write(
            f"{fire.latitude}\t{fire.longitude}\t{fire.bright_ti4}\t{fire.frp}\t{fire.acq_date}\t{fire.acq_time}\n"
        )

# Create interactive map visualization
if likely_fires:
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
            for fire in likely_fires
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
        title=f"Fire Detections in Iran ({len(likely_fires)} fires)",
        height=700,
    )

    # Save map as HTML
    map_filename = f"output/nasa_firms_fires_map_{timestamp}.html"
    fig.write_html(map_filename)
    print(f"Map saved to {map_filename}")

    # Show the map
    fig.show()
else:
    print("No fires detected.")
