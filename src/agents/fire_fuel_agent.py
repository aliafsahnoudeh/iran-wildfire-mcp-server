from src.domains.google_earth_engine import get_worldcover_class, init_earth_engine
from src.domains.planetary_computer import is_wildfire_fuel_potential


class FireFuelAgent:
    """Agent to check if a location is within a forest."""

    _is_google_earth_engine_initialized = False

    def __init__(self):
        pass

    def is_fire_fuel(self, latitude: float, longitude: float) -> bool:
        """Check if the given latitude and longitude are in a potential wildfire fuel area.

        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
        Returns:
            bool: True if the location is in a potential wildfire fuel area, False otherwise.
        """
        fuel_possible, _ = is_wildfire_fuel_potential(lat=latitude, lon=longitude)
        return fuel_possible

    def get_worldcover_class(
        self, latitude: float, longitude: float, scale: int = 10
    ) -> int:
        """Get the WorldCover class for the given latitude and longitude.

        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
            scale (int): Scale in meters.
        Returns:
            int: WorldCover class code.
        """
        if not self._is_google_earth_engine_initialized:
            init_earth_engine()
            self._is_google_earth_engine_initialized = True

        return get_worldcover_class(latitude=latitude, longitude=longitude, scale=scale)
