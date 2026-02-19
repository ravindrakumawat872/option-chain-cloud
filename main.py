import requests
import json

url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

session = requests.Session()

# First request to get cookies
session.get("https://www.nseindia.com", headers=headers)

# Actual data request
response = session.get(url, headers=headers)

try:
    data = response.json()
except:
    print("❌ Failed to fetch JSON data")
    print(response.text)
    exit()

if "records" not in data:
    print("❌ 'records' key not found")
    print(data)
    exit()

records = data["records"]["data"]

print("✅ Data fetched successfully")
print("Total strikes:", len(records))
