from dataclasses import dataclass


@dataclass
class MainWeatherData:
    """Main weather parameters."""

    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    sea_level: int
    grnd_level: int
    humidity: int
    temp_kf: float


@dataclass
class Weather:
    """Weather condition."""

    id: int
    main: str
    description: str
    icon: str


@dataclass
class Clouds:
    """Cloudiness data."""

    all: int


@dataclass
class Wind:
    """Wind data."""

    speed: float
    deg: int
    gust: float


@dataclass
class Rain:
    """Rain volume data."""

    three_h: float  # 3h field mapped to three_h

    @classmethod
    def from_dict(cls, data: dict) -> "Rain":
        """Create Rain from dict, handling '3h' key."""
        return cls(three_h=data.get("3h", 0.0))


@dataclass
class Snow:
    """Snow volume data."""

    three_h: float  # 3h field mapped to three_h

    @classmethod
    def from_dict(cls, data: dict) -> "Snow":
        """Create Snow from dict, handling '3h' key."""
        return cls(three_h=data.get("3h", 0.0))


@dataclass
class Sys:
    """System data."""

    pod: str  # Part of day (n - night, d - day)


@dataclass
class ForecastItem:
    """Individual forecast data point."""

    dt: int
    main: MainWeatherData
    weather: list[Weather]
    clouds: Clouds
    wind: Wind
    pop: float
    sys: Sys
    dt_txt: str
    visibility: int | None = None
    rain: Rain | None = None
    snow: Snow | None = None


@dataclass
class Coord:
    """City coordinates."""

    lat: float
    lon: float


@dataclass
class City:
    """City information."""

    id: int
    name: str
    coord: Coord
    country: str
    population: int
    timezone: int
    sunrise: int
    sunset: int


@dataclass
class ForecastResponse:
    """OpenWeatherMap 5-day forecast API response."""

    cod: str
    message: int
    cnt: int
    list: list[ForecastItem]
    city: City

    @classmethod
    def from_dict(cls, data: dict) -> "ForecastResponse":
        """Create ForecastResponse from dict."""
        forecast_items = [
            ForecastItem(
                dt=item["dt"],
                main=MainWeatherData(**item["main"]),
                weather=[Weather(**w) for w in item["weather"]],
                clouds=Clouds(**item["clouds"]),
                wind=Wind(**item["wind"]),
                visibility=item.get("visibility"),
                pop=item["pop"],
                sys=Sys(**item["sys"]),
                dt_txt=item["dt_txt"],
                rain=Rain.from_dict(item.get("rain", {})) if "rain" in item else None,
                snow=Snow.from_dict(item.get("snow", {})) if "snow" in item else None,
            )
            for item in data["list"]
        ]
        city = City(
            id=data["city"]["id"],
            name=data["city"]["name"],
            coord=Coord(**data["city"]["coord"]),
            country=data["city"]["country"],
            population=data["city"]["population"],
            timezone=data["city"]["timezone"],
            sunrise=data["city"]["sunrise"],
            sunset=data["city"]["sunset"],
        )
        return cls(
            cod=data["cod"],
            message=data["message"],
            cnt=data["cnt"],
            list=forecast_items,
            city=city,
        )

    def to_human_readable(self) -> str:
        """Convert forecast data to human-readable format."""
        output = []
        output.append(
            f"5-Day Weather Forecast for {self.city.name}, {self.city.country}"
        )
        for item in self.list:
            from datetime import datetime

            timestamp = datetime.fromtimestamp(item.dt).strftime("%Y-%m-%d %H:%M:%S")
            weather_desc = ", ".join(
                [f"{w.main} ({w.description})" for w in item.weather]
            )
            rain_volume = item.rain.three_h if item.rain else 0.0
            snow_volume = item.snow.three_h if item.snow else 0.0

            output.append(f"Timestamp: {timestamp}")
            output.append(f"Weather: {weather_desc}")
            output.append(
                f"Temperature: {item.main.temp}K (Feels like: {item.main.feels_like}K)"
            )
            output.append(f"Humidity: {item.main.humidity}%")
            output.append(f"Wind: {item.wind.speed} m/s at {item.wind.deg}°")
            output.append(f"Cloudiness: {item.clouds.all}%")
            output.append(
                f"Visibility: {item.visibility} meters"
                if item.visibility is not None
                else "Visibility: N/A"
            )
            output.append(f"Precipitation Probability: {item.pop * 100}%")
            output.append(f"Rain Volume (last 3h): {rain_volume} mm")
            output.append(f"Snow Volume (last 3h): {snow_volume} mm")
            output.append("-" * 20)

        return "\n".join(output)


@dataclass
class AirQualityMain:
    """Air Quality Index."""

    aqi: int  # Air Quality Index (1-5): 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor


@dataclass
class AirPollutionComponents:
    """Concentrations of air pollutants (μg/m³)."""

    co: float  # Carbon monoxide
    no: float  # Nitrogen monoxide
    no2: float  # Nitrogen dioxide
    o3: float  # Ozone
    so2: float  # Sulphur dioxide
    pm2_5: float  # Fine particles matter
    pm10: float  # Coarse particulate matter
    nh3: float  # Ammonia


@dataclass
class AirPollutionItem:
    """Individual air pollution data point."""

    dt: int  # Unix timestamp
    main: AirQualityMain
    components: AirPollutionComponents


@dataclass
class AirPollutionResponse:
    """OpenWeatherMap Air Pollution API response."""

    coord: dict[str, float]  # {'lon': longitude, 'lat': latitude}
    list: list[AirPollutionItem]

    @classmethod
    def from_dict(cls, data: dict) -> "AirPollutionResponse":
        """Create AirPollutionResponse from dict."""
        pollution_items = [
            AirPollutionItem(
                dt=item["dt"],
                main=AirQualityMain(**item["main"]),
                components=AirPollutionComponents(**item["components"]),
            )
            for item in data["list"]
        ]
        return cls(coord=data["coord"], list=pollution_items)

    def to_human_readable(self) -> str:
        """Convert air pollution data to human-readable format."""
        aqi_labels = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor",
        }

        output = []
        lon, lat = self.coord["lon"], self.coord["lat"]
        output.append(f"Air Pollution Data for Location: [{lat:.4f}°N, {lon:.4f}°E]")

        for item in self.list:
            from datetime import datetime

            timestamp = datetime.fromtimestamp(item.dt).strftime("%Y-%m-%d %H:%M:%S")
            aqi_label = aqi_labels.get(item.main.aqi, "Unknown")

            output.append(f"Timestamp: {timestamp}")
            output.append(f"Air Quality Index: {item.main.aqi} ({aqi_label})")
            output.append("\nPollutant Concentrations (μg/m³):")
            output.append(f"  CO (Carbon Monoxide):        {item.components.co:>10.2f}")
            output.append(f"  NO (Nitrogen Monoxide):      {item.components.no:>10.2f}")
            output.append(
                f"  NO₂ (Nitrogen Dioxide):      {item.components.no2:>10.2f}"
            )
            output.append(f"  O₃ (Ozone):                  {item.components.o3:>10.2f}")
            output.append(
                f"  SO₂ (Sulphur Dioxide):       {item.components.so2:>10.2f}"
            )
            output.append(
                f"  PM2.5 (Fine Particles):      {item.components.pm2_5:>10.2f}"
            )
            output.append(
                f"  PM10 (Coarse Particles):     {item.components.pm10:>10.2f}"
            )
            output.append(
                f"  NH₃ (Ammonia):               {item.components.nh3:>10.2f}"
            )
            output.append("-" * 20)

        return "\n".join(output)


@dataclass
class ReverseGeocodingLocation:
    """Location information from reverse geocoding."""

    name: str
    lat: float
    lon: float
    country: str
    state: str | None = None
    local_names: dict[str, str] | None = None


@dataclass
class ReverseGeocodingResponse:
    """OpenWeatherMap Reverse Geocoding API response (list of locations)."""

    locations: list[ReverseGeocodingLocation]

    @classmethod
    def from_dict(cls, data: list[dict]) -> "ReverseGeocodingResponse":
        """Create ReverseGeocodingResponse from list of dicts."""
        locations = [
            ReverseGeocodingLocation(
                name=item["name"],
                lat=item["lat"],
                lon=item["lon"],
                country=item["country"],
                state=item.get("state"),
                local_names=item.get("local_names"),
            )
            for item in data
        ]
        return cls(locations=locations)

    def to_human_readable(self) -> str:
        """Convert reverse geocoding data to human-readable format."""
        output = []
        for loc in self.locations:
            output.append(f"Location Name: {loc.name}")
            output.append(f"Country: {loc.country}")
            if loc.state:
                output.append(f"State: {loc.state}")
            output.append(f"Coordinates: [{loc.lat:.4f}°N, {loc.lon:.4f}°E]")
        return "\n".join(output)
