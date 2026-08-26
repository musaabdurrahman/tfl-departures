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
                background: #000;
                color: white;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 40px;
            }

            .board {
                max-width: 1000px;
                margin: auto;
                background: #111;
                border: 3px solid #333;
            }

            .header {
                padding: 25px 30px;
                border-bottom: 3px solid #333;
            }

            .station {
                font-size: 36px;
                font-weight: bold;
            }

            .subtitle {
                color: #aaa;
                margin-top: 8px;
            }

            .line {
                font-size: 16px;
                line-height: 1.2;
            }

            .column-headings {
                display: grid;
                grid-template-columns: 150px 1fr 220px 80px;
                padding: 0 10px 10px 10px;
                margin-top: 25px;
                color: #aaa;
                font-size: 14px;
            }

            .train {
                display: grid;
                grid-template-columns: 120px 1fr 220px 80px;
                align-items: center;
                padding: 18px 10px;
                border-bottom: 1px solid #555;
                font-size: 20px;
            }

            .destination {
                font-weight: bold;
            }

            .platform {
                color: #ccc;
            }

            .time {
                font-weight: bold;
                text-align: right;
            }

            .live {
                padding: 15px 30px;
                color: #aaa;
                font-size: 14px;
            }
        </style>
    </head>

    <body>

        <div class="board">

            <div class="header">
            
                <div class="station">King's Cross St. Pancras</div>
            
                <div class="subtitle">Live departures</div>

                
                    <div style="margin-top: 15px;">
                        <label for="station">Station: </label>
                    
                        <select id="station" onchange="changeStation()">
                            <option value="940GZZLUKSX">King's Cross St. Pancras</option>
                            <option value="940GZZLUASL">Arsenal</option>
                            <option value="940GZZLUVIC">Victoria</option>
                        </select>
                    </div>
            
                    <div style="margin-top: 15px;">
                        <label for="platform">Platform: </label>

                    <select id="platform" onchange="loadDepartures()">
                        <option value="">All platforms</option>
                    </select>
                </div>
            
            </div>

            <div class="column-headings">
                <span>LINE</span>
                <span>DESTINATION</span>
                <span>PLATFORM</span>
                <span>TIME</span>
            </div>

            <div id="departures">
                Loading departures...
            </div>

            <div class="live">
                ● LIVE — Updates every 30 seconds
            </div>

        </div>

        <script>

            async function loadDepartures() {

                const station = document.getElementById("station").value;
                const platform = document.getElementById("platform").value;
                
                let url = "/departures?station=" + station;


                if (platform) {
                    url += "&platform=" + encodeURIComponent(platform);
                }

                const response = await fetch(url);
                const trains = await response.json();

                const container = document.getElementById("departures");

                if (trains.error) {
                    container.innerHTML = `
                        <div class="train">
                            <span>Unable to load departures</span>
                        </div>
                    `;
                    return;
                }


                container.innerHTML = "";

                trains.forEach(train => {

                    const minutes = Math.floor(
                        train.timeToStation / 60
                    );

                    let time;

                    if (train.timeToStation < 60) {
                        time = "Due";
                    } else {
                        time = minutes + " min";
                    }

                    container.innerHTML += `
                        <div class="train">
                        
                            <span class="line">
                                ${train.line}
                            </span>
                        
                            <span class="destination">
                                ${train.destination}
                            </span>
                        
                            <span class="platform">
                                ${train.platform}
                            </span>
                        
                            <span class="time">
                                ${time}
                            </span>
                        
                        </div>
                    `;
                });
            }

            async function changeStation() {
            
                const station = document.getElementById("station");
            
                const stationName =
                    station.options[station.selectedIndex].text;
            
                document.querySelector(".station").textContent = stationName;
            
                await loadPlatforms();
            
                await loadDepartures();
            }


            async function loadPlatforms() {
            
                const station = document.getElementById("station").value;
            
                const response = await fetch(
                    "/departures?station=" + station
                );
            
                const trains = await response.json();

                
                const select = document.getElementById("platform");
            
                select.innerHTML = `
                    <option value="">All platforms</option>
                `;
            
                const platforms = [
                    ...new Set(trains.map(train => train.platform))
                ];
            
                platforms.forEach(platform => {
            
                    const option = document.createElement("option");
            
                    option.value = platform;
                    option.textContent = platform;
            
                    select.appendChild(option);
                });
            }
            
            loadDepartures();
            loadPlatforms();
            setInterval(loadDepartures, 30000);

        </script>

    </body>
    </html>
    """
@app.get("/departures")
def get_departures(
    station: str = "940GZZLUKSX",
    platform: str = None
):

    url = f"https://api.tfl.gov.uk/StopPoint/{station}/Arrivals"

    params = {
        "app_key": api_key
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {"error": "Unable to get departures from TfL"}
    
    data = response.json()

    if platform:
        data = [
            train for train in data
            if train.get("platformName") == platform
        ]

    data.sort(key=lambda train: train["timeToStation"])

    departures = []

    for train in data[:3]:

        departures.append({
            "destination": train.get(
                "destinationName",
                train.get("towards", "Unknown")
            ),
            "platform": train.get("platformName", "Unknown"),
            "line": train.get("lineName", "Unknown"),
            "timeToStation": train["timeToStation"]
        })

    return departures