import os

from dotenv import load_dotenv

load_dotenv()
MAP_KEY = os.getenv("FIRMS_API_KEY")

import pandas as pd
import requests

url = "https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY=" + MAP_KEY
try:
    response = requests.get(url)
    data = response.json()
    df = pd.Series(data)
    print(df)
except:
    # possible error, wrong MAP_KEY value, check for extra quotes, missing letters
    print("There is an issue with the query. \nTry in your browser: %s" % url)
