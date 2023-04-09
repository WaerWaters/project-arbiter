import requests

url = "https://server.jpgstoreapis.com/collection/fec7dfa59902eb40f65a62812662769962d5662f2a6bc2804b829881/transactions"

# Set query parameters
params = {
    "page": 1,
    "count": 10,
    "name": "",
    "traits": "e30="
}

# Make the GET request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    print(data["transactions"][0])
    print(data["transactions"][0]["asset_id"])
else:
    print(f"Error: {response.status_code}")







