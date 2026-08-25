from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = FastAPI()

api_key = os.getenv("TFL_API_KEY")


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TfL Departures</title>

        <style>
            body {
                background: #111;
                color: white;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 40px;
            }

            .board {
                max-width: 900px;
                margin: auto;
                background: #222;
                padding: 30px;
                border-radius: 10px;
            }

            h1 {
                margin-top: 0;
            }

            .train {
                display: flex;
                justify-content: space-between;
                padding: 18px 10px;
                border-bottom: 1px solid #555;
                font-size: 20px;
            }

            .time {
                font-weight: bold;
            }

            .live {
                margin-top: 20px;
                color: #aaa;
            }
        </style>
    </head>

    <body>

        <div class="board">

            <h1>Arsenal</h1>

            <div id="departures">
                Loading departures...
            </div>

            <div class="live">
                ● LIVE
            </div>

        </div>

        <script>

            async function loadDepartures() {

                const response = await fetch("/departures");
                const trains = await response.json();

                const container = document.getElementById("departures");

                container.innerHTML = "";

                trains.forEach(train => {

                    const minutes = Math.floor(train.timeToStation / 60);

                    let time;

                    if (train.timeToStation < 60) {
                        time = "Due";
                    } else {
                        time = minutes + " min";
                    }

                    container.innerHTML += `
                        <div class="train">
                            <span>${train.destination}</span>
                            <span>${time}</span>
                        </div>
                    `;
                });
            }

            loadDepartures();

            setInterval(loadDepartures, 30000);

        </script>

    </body>
    </html>
    """


@app.get("/departures")
def get_departures():

    url = "https://api.tfl.gov.uk/StopPoint/940GZZLUKSX/Arrivals"

    params = {
        "app_key": api_key
    }

    response = requests.get(url, params=params)

    data = response.json()

    data.sort(key=lambda train: train["timeToStation"])

    departures = []

    for train in data[:3]:

        departures.append({
            "destination": train.get(
                "destinationName",
                train.get("towards", "Unknown")
            ),
            "platform": train["platformName"],
            "timeToStation": train["timeToStation"]
        })

    return departures