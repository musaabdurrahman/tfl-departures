import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TFL_API_KEY")

url = "https://api.tfl.gov.uk/StopPoint/Mode/tube"

response = requests.get(
    url,
    params={"app_key": api_key}
)

print(response.status_code)

data = response.json()

print("Response type:", type(data))
print("Keys:", data.keys())

print("\nResponse:")
print(data)