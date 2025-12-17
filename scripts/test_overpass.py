import requests


def is_forest(lat, lon):
    query = f"""
    [out:json][timeout:25];
    (
    nwr(around:800,{lat},{lon})["natural"="wood"];
    nwr(around:800,{lat},{lon})["landuse"="forest"];
    nwr(around:800,{lat},{lon})["landcover"="trees"];
    );
    out tags center;
    """

    url = "https://overpass-api.de/api/interpreter"
    r = requests.post(url, data={"data": query})
    data = r.json()
    return len(data["elements"]) > 0


lat, lon = 26.35605, 61.29237
print("Forest nearby?", is_forest(lat, lon))
