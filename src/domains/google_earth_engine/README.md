# Google Earth Engine Integration

This module provides functions to access Earth Engine datasets for wildfire analysis.

## Setup

### 1. Authenticate

Run this command once in an active environment to authenticate with your Google Earth Engine account:

```bash
earthengine authenticate
```

This will open a browser window for you to log in and generate credentials.

### 2. Get Your Project ID

- Go to [Google Earth Engine Console](https://console.cloud.google.com/earth-engine)
- Note your project ID (shown in the console)

## Usage

```python
import datetime as dt
from src.agents.google_earth_engine import (
    init_earth_engine,
    get_worldcover_class,
    get_modis_ndvi_timeseries,
    get_gfwed_fwi_timeseries,
)

# Initialize once at the start of your application
init_earth_engine(project='your-project-id')

# Example coordinates (Tehran)
latitude, longitude = 35.6892, 51.3890

# Get land cover classification
land_cover = get_worldcover_class(latitude, longitude, year=2021)
print(f"Land cover class: {land_cover}")

# Get NDVI time series for the past 30 days
end_date = dt.date.today()
start_date = end_date - dt.timedelta(days=30)
ndvi_df = get_modis_ndvi_timeseries(latitude, longitude, start_date, end_date)
print(ndvi_df)

# Fire Weather Index (requires paid Climate Engine Pro subscription)
fwi_df = get_gfwed_fwi_timeseries(latitude, longitude, start_date, end_date)
```

## Available Functions

### `init_earth_engine(project)`

Initialize the Earth Engine API. Must be called once before using other functions.

**Parameters:**

- `project` (str): Your Google Earth Engine project ID
- `service_account` (str, optional): Service account email for authentication
- `key_path` (str, optional): Path to service account key file

### `get_worldcover_class(latitude, longitude, year=2021, scale=10)`

Get ESA WorldCover land cover classification at a point.

**Parameters:**

- `latitude`, `longitude` (float): Location coordinates in WGS84
- `year` (int): Year (2021 only for free accounts)
- `scale` (int): Sampling resolution in meters (default: 10m)

**Returns:** Land cover class code (int) or None

**Land Cover Classes:**

- 10: Tree cover
- 20: Shrubland
- 30: Grassland
- 40: Cropland
- 50: Built-up
- 60: Bare / sparse vegetation
- 70: Snow and ice
- 80: Permanent water bodies
- 90: Herbaceous wetland
- 95: Mangroves
- 100: Moss and lichen

### `get_modis_ndvi_timeseries(latitude, longitude, start, end, scale=250)`

Get MODIS NDVI time series for vegetation monitoring.

**Parameters:**

- `latitude`, `longitude` (float): Location coordinates
- `start`, `end` (date): Date range for data
- `scale` (int): Resolution in meters (default: 250m)

**Returns:** DataFrame with columns `["time", "ndvi"]`

**Note:** NDVI values are scaled by 10,000. To get actual NDVI: `ndvi_actual = ndvi / 10000`

### `get_gfwed_fwi_timeseries(latitude, longitude, start, end, scale=50000)`

Get Fire Weather Index time series (requires Climate Engine Pro subscription).

**Parameters:**

- `latitude`, `longitude` (float): Location coordinates
- `start`, `end` (date): Date range for data
- `scale` (int): Resolution in meters (default: 50km)

**Returns:** DataFrame with columns `["time", "FWI"]` (empty if not accessible)

**Note:** This dataset requires a paid Climate Engine Pro subscription and will return an empty DataFrame with a warning for free accounts.

## Data Availability

| Dataset        | Provider       | Latest Data | Free Access  |
| -------------- | -------------- | ----------- | ------------ |
| ESA WorldCover | ESA            | 2021        | ✅ Yes       |
| MODIS NDVI     | NASA           | Nov 2025    | ✅ Yes       |
| GFWED FWI      | Climate Engine | Current     | ❌ Paid only |

## Documentation

- [Google Earth Engine Datasets Catalog](https://developers.google.com/earth-engine/datasets/catalog)
- [ESA WorldCover v200](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200)
- [MODIS NDVI (MOD13Q1.061)](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1)
- [Earth Engine Python API Guide](https://developers.google.com/earth-engine/guides/python_install)
- [Earth Engine Authentication](https://developers.google.com/earth-engine/guides/auth)

## Limitations

- **ESA WorldCover**: Only 2021 data available for free accounts
- **MODIS NDVI**: 250m resolution, 16-day temporal resolution
- **GFWED FWI**: Requires paid subscription, not available for free accounts
