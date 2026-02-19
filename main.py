import requests
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

# ===== GOOGLE SHEETS SETUP =====

SPREADSHEET_ID = "1s5Notsc-o1eiqTzMdq-l6XRKE67Bfly8kNwkHo6fhUY"
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

# ===== FETCH OPTION CHAIN =====

url = f"https://www.nseindia.com/api/option-chain-indices?symbol={stock_name}"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers)
response = session.get(url, headers=headers)

data = response.json()

records = data["records"]
expiry = records["expiryDates"][0]
spot = records["underlyingValue"]

option_data = records["data"]

rows = []

for item in option_data:
    if item.get("expiryDate") == expiry:
        strike = item["strikePrice"]

        ce_ltp = ""
        pe_ltp = ""

        if "CE" in item:
            ce_ltp = item["CE"].get("lastPrice", "")

        if "PE" in item:
            pe_ltp = item["PE"].get("lastPrice", "")

        rows.append([
            stock_name,
            expiry,
            spot,
            strike,
            ce_ltp,
            pe_ltp
        ])

# ===== CLEAR & UPDATE SHEET =====

sheet.clear()

sheet.append_row(["Stock", "Expiry", "SPOT", "STRIKE", "CE LTP", "PE LTP"])

sheet.append_rows(rows)

print("Sheet updated successfully!")