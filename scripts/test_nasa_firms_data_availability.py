import os

import pandas as pd
from dotenv import load_dotenv

print("[INFO] Loading .env file...")
load_dotenv()
MAP_KEY = os.getenv("FIRMS_API_KEY")

# this url will return information about all supported sensors and their corresponding datasets
# instead of 'all' you can specify individual sensor, ex:LANDSAT_NRT
da_url = (
    "https://firms.modaps.eosdis.nasa.gov/api/data_availability/csv/" + MAP_KEY + "/all"
)
df = pd.read_csv(da_url)
print(df)
