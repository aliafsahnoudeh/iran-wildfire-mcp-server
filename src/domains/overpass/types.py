"""Data types for Overpass API forest checking with caching."""

from dataclasses import dataclass


@dataclass
class CacheConfig:
    """Configuration for the Overpass API cache system.

    Conservative defaults optimized for wildfire detection accuracy:
    - Fine grid precision minimizes location quantization errors
    - Large search radius ensures forest detection even with quantization
    - Cache never expires automatically - only updated via manual refresh_cache()

    Attributes:
        grid_precision: Decimal places for lat/lon grid rounding
            (default 0.001° ≈ 111m at 30° latitude, conservative for accuracy)
        search_radius: Radius in meters to search for forest features
            (default 1500m, larger for safety margin)
    """

    grid_precision: float = 0.001  # ~111m for accuracy
    search_radius: int = 1500  # Larger radius for safety

    def quantize_coordinate(self, coord: float) -> float:
        """Truncate a coordinate to grid precision.

        Args:
            coord: Latitude or longitude value

        Returns:
            Truncated coordinate value (keeps first N decimal places)
        """
        # Determine decimal places from precision (e.g., 0.001 -> 3 places)
        decimal_places = len(str(self.grid_precision).split(".")[-1].rstrip("0"))
        # Simple truncation to N decimal places
        import math

        multiplier = 10**decimal_places
        truncated = math.trunc(coord * multiplier) / multiplier
        return truncated

    def get_cache_key(self, lat: float, lon: float) -> str:
        """Generate cache key for a location.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Cache key string in format "lat_lon_radius"
        """
        grid_lat = self.quantize_coordinate(lat)
        grid_lon = self.quantize_coordinate(lon)
        return f"{grid_lat:.5f}_{grid_lon:.5f}_{self.search_radius}"


@dataclass
class CacheEntry:
    """A single cache entry for forest check results.

    Attributes:
        grid_lat: Quantized latitude for grid cell
        grid_lon: Quantized longitude for grid cell
        is_forest: Whether the location is forested
        last_checked: ISO timestamp of when the check was performed
        search_radius: Radius used for the forest search
        element_count: Number of OSM elements found (for debugging)
    """

    grid_lat: float
    grid_lon: float
    is_forest: bool
    last_checked: str
    search_radius: int
    element_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "CacheEntry":
        """Create CacheEntry from dictionary.

        Args:
            data: Dictionary with cache entry data

        Returns:
            CacheEntry instance
        """
        return cls(
            grid_lat=data["grid_lat"],
            grid_lon=data["grid_lon"],
            is_forest=data["is_forest"],
            last_checked=data["last_checked"],
            search_radius=data["search_radius"],
            element_count=data.get("element_count", 0),
        )

    def to_dict(self) -> dict:
        """Convert CacheEntry to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            "grid_lat": self.grid_lat,
            "grid_lon": self.grid_lon,
            "is_forest": self.is_forest,
            "last_checked": self.last_checked,
            "search_radius": self.search_radius,
            "element_count": self.element_count,
        }
