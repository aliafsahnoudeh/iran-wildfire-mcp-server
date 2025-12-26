from dataclasses import dataclass
from enum import Enum


class DayNight(str, Enum):
    DAY = "D"
    NIGHT = "N"


class Confidence(str, Enum):
    LOW = "l"
    NOMINAL = "n"
    HIGH = "h"


class BoundingBox:
    """Geographical bounding box defined by min and max latitudes and longitudes."""

    def __init__(
        self,
        min_latitude: float,
        max_latitude: float,
        min_longitude: float,
        max_longitude: float,
    ):
        self.min_latitude = min_latitude
        self.max_latitude = max_latitude
        self.min_longitude = min_longitude
        self.max_longitude = max_longitude

    def to_string(self) -> str:
        """Convert bounding box to string format required by NASA FIRMS API."""
        return f"{self.min_latitude},{self.min_longitude},{self.max_latitude},{self.max_longitude}"


@dataclass
class RawFireData:
    latitude: float  # Center latitude of the detected fire pixel
    longitude: float  # Center longitude of the detected fire pixel
    bright_ti4: float  # Brightness temperature (Kelvin) in MODIS/VIIRS band I4/T4
    scan: float  # Scan pixel size (degrees)
    track: float  # Track pixel size (degrees)
    acq_date: str  # Acquisition date (YYYY-MM-DD)
    acq_time: str  # Acquisition time (HHMM, UTC)
    satellite: str  # Satellite name (e.g., "Aqua", "Terra", "N20")
    instrument: str  # Instrument name (e.g., "MODIS", "VIIRS")
    confidence: str  # Detection confidence: 'l' (low), 'n' (nominal), 'h' (high), or percent string
    version: str  # Processing version (e.g., "2.0NRT")
    bright_ti5: float  # Brightness temperature (Kelvin) in MODIS/VIIRS band I5/T5
    frp: float  # Fire Radiative Power (MW)
    daynight: DayNight  # 'D' for day, 'N' for night detection

    def to_human_readable(self, index: int | None = None) -> str:
        """Convert fire data to a human-readable format."""
        # Parse acquisition time (HHMM format)
        time_str = str(self.acq_time).zfill(4)  # Ensure 4 digits
        hour = time_str[:2]
        minute = time_str[2:]

        # Format confidence
        confidence_map = {"l": "Low", "n": "Nominal", "h": "High"}
        confidence_display = confidence_map.get(self.confidence, f"{self.confidence}%")

        # Format day/night
        daynight_display = "Day" if self.daynight == DayNight.DAY else "Night"

        # Convert Kelvin to Celsius for readability
        temp_ti4_c = self.bright_ti4 - 273.15
        temp_ti5_c = self.bright_ti5 - 273.15

        return f"""Location: {self.latitude:.4f}°, {self.longitude:.4f}°
Detection Time: {self.acq_date} at {hour}:{minute} UTC ({daynight_display})
Satellite: {self.satellite} ({self.instrument})
Confidence: {confidence_display}

Fire Characteristics:
  - Fire Radiative Power: {self.frp:.2f} MW
  - Brightness Temp (Band I4/T4): {temp_ti4_c:.1f}°C ({self.bright_ti4:.1f}K)
  - Brightness Temp (Band I5/T5): {temp_ti5_c:.1f}°C ({self.bright_ti5:.1f}K)
  - Pixel Size: {self.scan:.3f}° × {self.track:.3f}°

Data Version: {self.version}"""
