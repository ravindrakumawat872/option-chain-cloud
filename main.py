import requests
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------------------
# Google Auth from Secret
# ---------------------------

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ---------------------------
# Open Sheet
# ---------------------------

SHEET_NAME = "OptionChain"   # <-- apni sheet ka exact naam
sheet = client.open(SHEET_NAME).sheet1

symbol = sheet.acell("A2").value

print("Fetching data for:", symbol)

# ---------------------------
# NSE Fetch
# ---------------------------

url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers)
response = session.get(url, headers=headers)

try:
    data = response.json()
except:
    print("Failed to fetch JSON")
    exit()

if "records" not in data:
    print("Records not found")
    exit()

records = data["records"]["data"]
expiry = data["records"]["expiryDates"][0]
spot = data["records"]["underlyingValue"]

# ---------------------------
# Write Header
# ---------------------------

sheet.update("A4:F4", [["Stock", "Expiry", "SPOT", "STRIKE", "CE LTP", "PE LTP"]])

row = 5

for item in records:
    strike = item.get("strikePrice")

    ce_ltp = item.get("CE", {}).get("lastPrice", "")
    pe_ltp = item.get("PE", {}).get("lastPrice", "")

    sheet.update(
        f"A{row}:F{row}",
        [[symbol, expiry, spot, strike, ce_ltp, pe_ltp]],
    )
    row += 1

print("Sheet Updated Successfully ✅")
