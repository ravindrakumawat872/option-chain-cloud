import requests
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ============ Google Sheets Setup ============

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("OptionChain").sheet1

symbol = sheet.acell("A2").value.strip().upper()

print(f"Fetching option chain for: {symbol}")

# ============ NSE API Fetch ============

base = "https://www.nseindia.com"
url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.get(base, headers=headers)

response = session.get(url, headers=headers)

try:
    data = response.json()
except Exception as e:
    print("❌ Cannot parse JSON:", e)
    print(response.text)
    exit()

if "records" not in data:
    print("❌ No option chain data found")
    exit()

records = data["records"]["data"]
expiry_list = data["records"]["expiryDates"]
underlying_value = data["records"]["underlyingValue"]

# choose nearest expiry (first in list)
expiry = expiry_list[0] if expiry_list else ""

# header write
sheet.update("A4:F4", [["Stock","Expiry","SPOT","STRIKE","CE LTP","PE LTP"]])

row = 5
for item in records:
    strike = item.get("strikePrice", "")
    ce_ltp = item.get("CE", {}).get("lastPrice", "")
    pe_ltp = item.get("PE", {}).get("lastPrice", "")

    sheet.update(f"A{row}:F{row}", [[symbol, expiry, underlying_value, strike, ce_ltp, pe_ltp]])
    row += 1

print("📊 Sheet updated successfully!")
