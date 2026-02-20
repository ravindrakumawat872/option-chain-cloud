import requests
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

# ===== GOOGLE SHEET CONFIG =====

SPREADSHEET_ID = "1s5Notsc-o1eiqTzMdq-I6XRKE67Bfly8kNwkHo6fhUY"
SHEET_NAME = "OptionChain"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# ===== READ STOCK NAME =====

stock_name = sheet.acell("A2").value

if not stock_name:
    print("No stock name found in A2")
    exit()

stock_name = stock_name.strip().upper()

# ===== NSE FETCH (Improved) =====

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive"
}

# First request to get cookies
session.get("https://www.nseindia.com", headers=headers, timeout=10)

# Determine correct endpoint
if stock_name in ["NIFTY", "BANKNIFTY", "FINNIFTY"]:
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={stock_name}"
else:
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={stock_name}"

response = session.get(url, headers=headers, timeout=10)

data = response.json()

if "records" not in data:
    print("NSE blocked request or invalid symbol")
    exit()

records = data["records"]
expiry = records["expiryDates"][0]
spot = records["underlyingValue"]

option_data = records["data"]

rows = []

for item in option_data:
    if item.get("expiryDate") == expiry:
        strike = item["strikePrice"]

        ce_ltp = item.get("CE", {}).get("lastPrice", "")
        pe_ltp = item.get("PE", {}).get("lastPrice", "")

        rows.append([
            stock_name,
            expiry,
            spot,
            strike,
            ce_ltp,
            pe_ltp
        ])

# ===== UPDATE SHEET =====

sheet.clear()

sheet.append_row(["Stock", "Expiry", "SPOT", "STRIKE", "CE LTP", "PE LTP"])
sheet.append_rows(rows)

print("Sheet updated successfully!")