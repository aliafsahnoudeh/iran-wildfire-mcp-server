import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domains.google_earth_engine.core import (
    get_worldcover_class,
    init_earth_engine,
)

latitude = 36.01993
longitude = 50.59037

init_earth_engine()

result = get_worldcover_class(
    latitude=latitude,
    longitude=longitude,
    year=2021,
    scale=10,
)
print(f"World Cover class at ({latitude}, {longitude}): {result}")
