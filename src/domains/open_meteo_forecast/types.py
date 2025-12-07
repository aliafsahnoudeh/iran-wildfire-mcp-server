from dataclasses import dataclass


@dataclass
class RawOpenMeteoCurrent:
    time: str  # ISO8601 timestamp of current data
    interval: int  # Interval in seconds
    temperature_2m: float  # Current temperature at 2m (°C)
    wind_speed_10m: float  # Current wind speed at 10m (km/h)


@dataclass
class RawOpenMeteoHourly:
    time: list[str]  # List of ISO8601 timestamps
    temperature_2m: list[float]  # Hourly temperature at 2m (°C)
    wind_speed_10m: list[float]  # Hourly wind speed at 10m (km/h)
    precipitation: list[float]  # Hourly precipitation (mm)
    relative_humidity_2m: list[float]  # Hourly relative humidity at 2m (%)


@dataclass
class RawOpenMeteoForecast:
    latitude: float  # Latitude of the forecast location
    longitude: float  # Longitude of the forecast location
    generationtime_ms: float  # Time to generate forecast (ms)
    utc_offset_seconds: int  # UTC offset in seconds
    timezone: str  # Timezone name (e.g., 'GMT')
    timezone_abbreviation: str  # Timezone abbreviation (e.g., 'GMT')
    elevation: float  # Elevation above sea level (m)
    current_units: dict[str, str]  # Units for current weather fields
    current: RawOpenMeteoCurrent  # Current weather data
    hourly_units: dict[str, str]  # Units for hourly weather fields
    hourly: RawOpenMeteoHourly  # Hourly weather data

    def __str__(self) -> str:
        """Return a human-readable string representation of the forecast."""
        lines = [
            "Weather Forecast",
            "=" * 60,
            f"Location: {self.latitude}°N, {self.longitude}°E",
            f"Elevation: {self.elevation}m",
            f"Timezone: {self.timezone} ({self.timezone_abbreviation})",
            "",
            "Current Weather:",
            "-" * 60,
        ]

        # Iterate over current_units and format with values
        current_dict = self.current.__dict__
        for key, unit in self.current_units.items():
            if key in current_dict:
                value = current_dict[key]
                # Format field name nicely
                field_name = key.replace("_", " ").title()
                lines.append(f"  {field_name}: {value} {unit}")

        lines.extend(
            [
                "",
                "Hourly Forecast:",
                "-" * 60,
                f"  Total data points: {len(self.hourly.time)}",
                f"  Time range: {self.hourly.time[0] if self.hourly.time else 'N/A'} to {self.hourly.time[-1] if self.hourly.time else 'N/A'}",
                "",
                "  Available variables:",
            ]
        )

        # Iterate over hourly_units to show what data is available
        hourly_dict = self.hourly.__dict__
        for key, unit in self.hourly_units.items():
            if key in hourly_dict and key != "time":
                values = hourly_dict[key]
                if values:
                    field_name = key.replace("_", " ").title()
                    min_val = min(values)
                    max_val = max(values)
                    avg_val = sum(values) / len(values)
                    lines.append(
                        f"    • {field_name}: {min_val:.1f} - {max_val:.1f} {unit} (avg: {avg_val:.1f} {unit})"
                    )

        lines.extend(
            [
                "",
                f"Generation time: {self.generationtime_ms:.2f}ms",
            ]
        )

        return "\n".join(lines)
