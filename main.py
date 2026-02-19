import requests
import pandas as pd

symbol = "NIFTY"

base_url = "https://www.nseindia.com"
api_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

session = requests.Session()

# First request to get cookies
session.get(base_url, headers=headers)

# Actual API request
response = session.get(api_url, headers=headers)

if response.status_code == 200:
    data = response.json()
    records = data["records"]["data"]

    rows = []

    for item in records:
        if "CE" in item and "PE" in item:
            rows.append({
                "Strike": item["strikePrice"],
                "CE_OI": item["CE"]["openInterest"],
                "PE_OI": item["PE"]["openInterest"]
            })

    df = pd.DataFrame(rows)

    print("Option Chain Data (Top 5 Rows):")
    print(df.head())

else:
    print("Failed to fetch data:", response.status_code)
