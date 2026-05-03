import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from environment variable or file
creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
if creds_json:
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    # Fallback to credentials.json if environment variable not set
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

gc = gspread.authorize(creds)

sheet = gc.open("S26 Merton Chores").sheet1

data = sheet.get_all_records()

print("First 2 rows:")
print(data[:2])

print("\nWeek label:")
print(sheet.acell("E2").value)