from src.domains.google_earth_engine import get_worldcover_class, init_earth_engine
from src.domains.overpass import is_forest


class ForestAgent:
    """Agent to check if a location is within a forest."""

    _is_google_earth_engine_initialized = False

    def __init__(self):
        pass

    def is_forest(
        self, latitude: float, longitude: float, search_radius: int = 1500
    ) -> bool:
        """Check if the given latitude and longitude are in a forest.

        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
            search_radius (int): Search radius in meters.
        Returns:
            bool: True if the location is in a forest, False otherwise.
        """
        return is_forest(lat=latitude, lon=longitude, search_radius=search_radius)

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
