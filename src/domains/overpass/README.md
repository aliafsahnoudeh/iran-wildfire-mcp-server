# Overpass API Domain

This domain provides cached forest checking using the Overpass API to query OpenStreetMap data.

## Overview

The Overpass API allows querying OpenStreetMap for geographic features. This implementation uses a **conservative caching strategy optimized for wildfire detection accuracy**.

### Forest Detection

**Checks if a location is forested** by searching for OSM features with tags:
- `natural=wood`
- `landuse=forest`
- `landcover=trees`

### Conservative Caching Strategy

**Designed to prioritize accuracy over performance** to avoid missing forest fires:

1. **Fine grid precision** (0.001° ≈ 111m at 30° latitude)
   - Minimizes location quantization errors
   - Ensures fire locations aren't shifted too far from actual coordinates
   
2. **Large search radius** (1500m instead of 800m)
   - Provides safety margin even with coordinate quantization
   - Ensures forests are detected even near grid cell boundaries

3. **Manual cache updates**:
   - Cache never expires automatically
   - Call `refresh_cache()` manually when you need fresh data
   - Gives you full control over when to update cached forest information

4. **Persistent JSON storage** with in-memory caching for performance

## Usage

### Basic Forest Check

```python
from src.domains.overpass import is_forest

# Check if location is forested (uses conservative defaults)
is_forested = is_forest(
    lat=35.6892,
    lon=51.3890
)

# Custom configuration (not recommended unless you have specific needs)
is_forested = is_forest(
    lat=35.6892,
    lon=51.3890,
    grid_precision=0.001,     # ~111m grid cells (default)
    search_radius=1500        # 1500m search radius (default)
)
```

### Manual Cache Refresh

```python
from src.domains.overpass import refresh_cache

# Update all cache entries with fresh data from Overpass API
stats = refresh_cache()
print(f"Updated {stats['updated']} entries, {stats['failed']} failures")

# Custom configuration
stats = refresh_cache(
    search_radius=1500,       # 1500m radius (default)
    delay_seconds=3           # Delay between API calls
)
```

**When to refresh cache:**
- Before wildfire season starts
- After major events that change forest coverage (fires, logging)
- Periodically (weekly/monthly depending on your accuracy needs)
- When you suspect OSM data has been updated

## Configuration

### Conservative Defaults (Recommended for Wildfire Detection)

**These defaults prioritize accuracy over performance:**

- **Grid Precision: 0.001°** (~111m at 30° latitude)
  - Fine granularity minimizes quantization errors
  - Fire at 35.6892° uses different cache than 35.6902°
  - ⚠️ Larger cache size but critical for accuracy

- **Search Radius: 1500m**
  - Large radius provides safety margin
  - Ensures forest detection even with coordinate quantization
  - Captures forests near grid cell boundaries

- **No Automatic Expiration**
  - Cache entries never expire automatically
  - You control when to refresh data via `refresh_cache()`
  - Eliminates risk of stale data causing false negatives during critical operations

### Why These Conservative Settings?

For wildfire detection, **missing a forest fire is much worse than extra API calls**:

1. **Fine grid prevents false negatives**: A fire near a forest shouldn't be quantized away from it
2. **Large radius catches edge cases**: Forests near boundaries are still detected
3. **Manual refresh ensures control**: You decide when data needs updating, not an arbitrary timer

### Custom Configuration (Advanced)

You can adjust these parameters if you have specific needs:

```python
# Example: Coarser grid (NOT recommended for wildfire detection)
is_forested = is_forest(
    lat=35.6892,
    lon=51.3890,
    grid_precision=0.01,      # Coarser ~1km grid
    search_radius=1000        # Smaller radius
)
```

⚠️ **Warning**: Relaxing these defaults may cause missed forest fires!

## Cache Storage

Cache is stored in JSON format at:
```
output/overpass_cache.json
```

Each entry contains:
- `grid_lat`, `grid_lon`: Quantized coordinates
- `is_forest`: Boolean result
- `last_checked`: ISO timestamp (informational only, not used for expiration)
- `search_radius`: Radius used for check
- `element_count`: Number of OSM elements found (for debugging)

## Rate Limiting

The Overpass API has rate limits. This implementation:
- Adds delays between successive calls (default 3 seconds)
- Uses exponential backoff for retries
- Maximum 5 retry attempts per location

## API Reference

### Overpass API

- **Endpoint**: `https://overpass-api.de/api/interpreter`
- **Method**: POST
- **Timeout**: 30 seconds
- **Documentation**: https://wiki.openstreetmap.org/wiki/Overpass_API

### Query Format

```
[out:json][timeout:25];
(
  nwr(around:1500,lat,lon)["natural"="wood"];
  nwr(around:1500,lat,lon)["landuse"="forest"];
  nwr(around:1500,lat,lon)["landcover"="trees"];
);
out tags center;
```

## Performance vs Accuracy Trade-offs

### Current Design (Conservative)

✅ **Prioritizes Accuracy**:
- Fine grid (111m) catches all fire locations accurately
- Large radius (1500m) ensures forest detection
- Manual refresh gives you control over data freshness
- **Result**: Minimal risk of missing forest fires

⚠️ **Performance Impact**:
- Larger cache file size (~10x more entries than 1km grid)
- All API calls on cache miss (no automatic refresh)
- Slightly slower cache lookups (more entries)

### Why This Trade-off Matters for Wildfire Detection

**Scenario: Fire near forest edge**
- **Coarse grid (0.01° = 1km)**: Fire at 35.6892° quantized to 35.69°
  - Could be 500m+ from actual location
  - Might miss forest if near edge
- **Fine grid (0.001° = 111m)**: Fire at 35.6892° quantized to 35.689°
  - Only ~50m from actual location
  - Catches forest even at edges

**The cost of a false negative (missing a forest fire) >> cost of extra API calls**

## Workflow Recommendations

### Initial Setup
```python
# First run - builds cache for your region
for fire in fires:
    is_forested = is_forest(fire.lat, fire.lon)
    # Cache builds automatically on first check
```

### Regular Maintenance
```python
# Run weekly/monthly to keep cache fresh
refresh_cache()
```

### Pre-Season Preparation
```python
# Before wildfire season, refresh all cached data
stats = refresh_cache()
logger.info(f"Pre-season refresh: {stats['updated']} locations updated")
```

## Environment Variables

No environment variables required. All configuration is parameter-based for flexibility.

## Notes

- **Conservative defaults are intentional** for wildfire safety
- **Manual refresh strategy** gives you full control over data freshness
- Grid-based approach provides spatial consistency
- OSM forest data is generally reliable and stable
- In-memory caching keeps repeated lookups fast
- Cache initialized once on module import for performance
- No automatic expiration eliminates surprise cache misses during critical operations
