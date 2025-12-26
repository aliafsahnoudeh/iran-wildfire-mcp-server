from src.domains.google_earth_engine import get_worldcover_class, init_earth_engine
from src.domains.planetary_computer import is_wildfire_fuel_potential


class FireFuelAgent:
    """Agent to check if a location is within a forest."""

    _is_google_earth_engine_initialized = False

    def __init__(self):
        pass

    def is_fire_fuel(
        self,
        lat: float,
        lon: float,
        window_size: int = 11,
        min_ratio: float = 0.4,
    ) -> bool:
        """Check if the given latitude and longitude are in a potential wildfire fuel area.
        Args:
          lat (float): Latitude of the location.
          lon (float): Longitude of the location.
          window_size (int): Size of the square window (in pixels) to analyze around the point.
          min_ratio (float): Minimum ratio of burnable land cover required to consider
                             the area as potential wildfire fuel.

        Returns:
            bool: True if the location is in a potential wildfire fuel area, False otherwise.
        """
        fuel_possible, _ = is_wildfire_fuel_potential(
            lat=lat, lon=lon, window_size=window_size, min_ratio=min_ratio
        )
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
