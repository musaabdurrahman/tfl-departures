import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TFL_API_KEY")

url = "https://api.tfl.gov.uk/StopPoint/940GZZLUKSX/Arrivals"

response = requests.get(
    url,
    params={"app_key": api_key}
)

print(response.status_code)

data = response.json()

platforms = sorted(
    set(
        train.get("platformName", "Unknown")
        for train in data
        if train.get("platformName")
    )
)

print("\nPLATFORMS:")
for platform in platforms:
    print(platform)