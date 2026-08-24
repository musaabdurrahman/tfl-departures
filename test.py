from dotenv import load_dotenv
import os
import requests

load_dotenv()

api_key = os.getenv("TFL_API_KEY")

url = "https://api.tfl.gov.uk/StopPoint/940GZZLUASL/Arrivals"

params = {
    "app_key": api_key
}

response = requests.get(url, params=params)

print(response.status_code)
print(response.json())