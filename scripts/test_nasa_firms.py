import logging
import os
import sys
from datetime import datetime
from pathlib import Path

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


likely_fires = get_fires_in_iran(start_date="2025-11-21", end_date="2025-11-21")

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
