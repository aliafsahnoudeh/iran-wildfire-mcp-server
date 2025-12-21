import requests


def is_fire_fuel(lat, lon, search_radius=1500, timeout=60) -> bool:
    # Fuel features (vegetation that can carry fire)
    fuel_query = f"""
      nwr(around:{search_radius},{lat},{lon})["natural"="wood"];
      nwr(around:{search_radius},{lat},{lon})["landuse"="forest"];
      nwr(around:{search_radius},{lat},{lon})["natural"="scrub"];
      nwr(around:{search_radius},{lat},{lon})["natural"="grassland"];
      nwr(around:{search_radius},{lat},{lon})["landcover"="trees"];
      nwr(around:{search_radius},{lat},{lon})["landcover"="grass"];
    """

    # Clear non-fuel / misleading features (water, bare ground, dense built-up)
    exclude_query = f"""
      nwr(around:{search_radius},{lat},{lon})["natural"="water"];
      nwr(around:{search_radius},{lat},{lon})["waterway"];
      nwr(around:{search_radius},{lat},{lon})["natural"="bare_rock"];
      nwr(around:{search_radius},{lat},{lon})["natural"="sand"];
      nwr(around:{search_radius},{lat},{lon})["landuse"~"^(residential|commercial|industrial|construction|quarry)$"];
      nwr(around:{search_radius},{lat},{lon})["building"];
      nwr(around:{search_radius},{lat},{lon})["highway"];
    """

    query = f"""
    [out:json][timeout:25];
    (
      {fuel_query}
      {exclude_query}
    );
    out tags qt;
    """

    url = "https://overpass-api.de/api/interpreter"
    headers = {"User-Agent": "Iran-Wildfire-MCP-Server/1.0"}

    r = requests.post(url, data={"data": query}, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    print("Overpass API raw response: %s", data)
    return len(data["elements"]) > 0


lat, lon = 36.686328, 54.005690
print("Is fire fuel nearby?", is_fire_fuel(lat, lon))
