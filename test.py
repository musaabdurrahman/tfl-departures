from dotenv import load_dotenv
import os
import requests

load_dotenv()

api_key = os.getenv("TFL_API_KEY")

url = "https://api.tfl.gov.uk/StopPoint/940GZZLUKSX/Arrivals"

params = {
    "app_key": api_key
}

response = requests.get(url, params=params)

print(response.status_code)

if response.status_code != 200:
    print("TfL API request failed")
    print(response.json())
    exit()

data = response.json()

print("Number of arrivals:", len(data))

data.sort(key=lambda train: train["timeToStation"])

platform = "Northbound - Platform 7"
line = "northern"

data = [
    train for train in data
    if train.get("platformName") == platform
    and train.get("lineId") == line
]
for train in data[:3]:
    seconds = train["timeToStation"]

    if seconds < 60:
        time = "Due"
    else:
        minutes = seconds // 60
        time = f"{minutes} min"

    destination = train.get(
        "destinationName",
        train.get("towards", "Unknown")
    )

    print(
        destination,
        "-",
        train["platformName"],
        "-",
        time
    )

#    print(
#        train["destinationName"],
#        "-",
#        train["platformName"],
#        "-",
#        time
#    )