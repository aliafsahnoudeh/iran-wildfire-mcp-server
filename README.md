# Wildfire MCP Server

A Model Context Protocol (MCP) server for detecting, monitoring, and analyzing potential wildfires globally using multiple data sources including NASA FIRMS, OpenWeatherMap, and Google Earth Engine.

## Overview

This MCP server provides AI assistants with tools to detect and analyze wildfire activity anywhere in the world by integrating real-time satellite data, weather forecasts, air pollution metrics, and geographical information. It's designed to help identify potential wildfires and assess their environmental impact.

## Features

- **Fire Detection**: Query NASA FIRMS (Fire Information for Resource Management System) for active fire hotspots
- **Weather Forecasting**: Get 5-day weather forecasts for specific locations
- **Air Pollution Monitoring**: Access current and historical air pollution data
- **Reverse Geocoding**: Convert coordinates to human-readable addresses
- **Fire Fuel Assessment**: Determine if a location contains potential wildfire fuel based on land cover data
- **Customizable Filtering**: Filter fires by radiative power, brightness temperature, and geographic boundaries

## Prerequisites

Configure API keys (if required):

- NASA FIRMS Map Key
- OpenWeatherMap API Key
- Google Earth Engine credentials (if applicable)

## Available Tools

### `get_potential_wildfires`

Get potential wildfires for a specific date using NASA FIRMS data.

**Parameters:**

- `date` (str, optional): Date in YYYY-MM-DD format. Defaults to current date.
- `frp` (float): Fire Radiative Power threshold (default: 1)
- `bright_ti4` (float): Brightness temperature threshold (default: 50)
- `in_iran` (bool): If True, filters fires to only show those within Iran's borders (useful for Iran-specific monitoring)
- `bounding_box` (BoundingBox, optional): Custom bounding box to limit search area to any geographic region

### `get_address`

Get the address for given coordinates.

**Parameters:**

- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location

### `get_weather_forecast`

Get 5-day weather forecast with 3-hour intervals.

**Parameters:**

- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location

### `get_current_air_pollution_data`

Fetch current air pollution data.

**Parameters:**

- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location

### `get_historical_air_pollution_data`

Fetch historical air pollution data for a date range.

**Parameters:**

- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location
- `start_date` (str): Start of period (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `end_date` (str): End of period (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)

### `is_fire_fuel`

Check if a location contains potential wildfire fuel.

**Parameters:**

- `latitude` (float): Latitude of the location
- `longitude` (float): Longitude of the location

**Returns:** Boolean indicating if location is in a potential wildfire fuel area

## Testing

### Using MCP Inspector

```bash
npx @modelcontextprotocol/inspector python wildfire_mcp_server.py
```

The timeout for the client needs to be increased since some data fetching operations can take a while. This can be done either by setting the config in the UI or by setting the following environment variables:

```bash
export MCP_SERVER_REQUEST_TIMEOUT=9000000
export MCP_REQUEST_MAX_TOTAL_TIMEOUT=9000000
export MCP_REQUEST_TIMEOUT_RESET_ON_PROGRESS=true
```

**Good date to test:** 2025-11-21 (known active fire day)

### Running Test Scripts

```bash
# Test individual components
uv run scripts/test_nasa_firms.py
uv run scripts/test_main_functionality.py
uv run scripts/test_overpass.py
```

## Architecture

The project is organized into several layers:

- **`wildfire_mcp_server.py`**: Main server entry point with MCP tool definitions
- **`src/agents/`**: High-level agent classes that orchestrate domain services
  - `LikelyFireAgent`: Fire detection and filtering
  - `FireFuelAgent`: Land cover and fuel assessment
  - `AddressAgent`: Reverse geocoding
  - `WeatherForecastAgent`: Weather data retrieval
  - `AirPollutionAgent`: Air quality data
- **`src/domains/`**: Domain-specific integrations
  - `nasa_firms/`: NASA FIRMS fire data API
  - `open_weather_map/`: Weather and air pollution APIs
  - `google_earth_engine/`: Land cover data
  - `overpass/`: OpenStreetMap data
  - `planetary_computer/`: Microsoft Planetary Computer integration

## Data Sources

- **NASA FIRMS**: Active fire data from MODIS and VIIRS satellites
- **OpenWeatherMap**: Weather forecasts and air pollution metrics
- **Google Earth Engine**: Land cover classification
- **OpenStreetMap (Overpass)**: Geographic and administrative boundaries

## License

This project is licensed under a custom Evaluation and Non-Production License. See the [LICENSE](LICENSE) file for details.

**Note**: Production use requires explicit written approval from the copyright holder.

## Contributing

Contributions are welcome for evaluation and improvement purposes. Please ensure any pull requests maintain the evaluation-only nature of this license.

## Disclaimer

This tool is designed for wildfire monitoring and research purposes. Fire detection data should be verified with official sources before taking any action. The accuracy of fire detection depends on satellite data availability and environmental conditions.

## Support

For issues, questions, or production licensing inquiries, please open an issue on the repository or contact the maintainers directly.
