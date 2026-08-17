import requests

url = "https://api.tfl.gov.uk/Line/Mode/tube/Status"

response = requests.get(url)

print(response.status_code)
print(response.json())

