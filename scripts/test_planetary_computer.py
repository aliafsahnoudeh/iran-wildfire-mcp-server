import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domains.planetary_computer import is_wildfire_fuel_potential

lat, lon = 36.013324, 53.267073
fuel_possible, burnable_ratio = is_wildfire_fuel_potential(lat, lon)
print(
    f"WorldCover fuel potential at ({lat}, {lon}): {fuel_possible} (burnable ratio {burnable_ratio})"
)
