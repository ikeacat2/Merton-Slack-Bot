import os
import json
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from slack_sdk import WebClient

# --- CONFIG ---
SPREADSHEET_NAME = "S26 Merton Chores"
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = "#chores"

if not SLACK_TOKEN:
    raise ValueError("SLACK_TOKEN environment variable not set")

# --- GOOGLE SHEETS SETUP ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from environment variable or file
creds_json = os.getenv("GOOGLE_CREDENTIALS")
if creds_json:
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    # Fallback to credentials.json if environment variable not set
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

gc = gspread.authorize(creds)

sheet = gc.open(SPREADSHEET_NAME).sheet1
data = sheet.get_all_records()

df = pd.DataFrame(data)

# --- GET WEEK LABEL ---
week_label = sheet.acell("E2").value

# --- CLEAN DATA ---
df["Completed"] = df["Completed"].astype(str).str.upper() == "TRUE"

# --- SUMMARY STATS ---
total = len(df)
completed = df["Completed"].sum()
percent = int((completed / total) * 100) if total > 0 else 0

# Per-person summary
summary = df.groupby("Name").agg(
    Chore_Count=("Chore", "count"),
    Completed_Count=("Completed", "sum")
).reset_index()

# Sort by performance (lowest first)
summary["Ratio"] = summary["Completed_Count"] / summary["Chore_Count"]
summary = summary.sort_values(by="Ratio")

# --- FORMAT MESSAGE (CLEAN VERSION) ---
message = f"🏠 *Chore Report — {week_label}*\n\n"

# Summary block
message += "📊 *Summary*\n"
message += f"• Completed: {completed} / {total}\n"
message += f"• Completion Rate: {percent}%\n\n"

# Needs attention
message += "⚠️ *Needs Attention*\n"
needs_attention = summary[summary["Completed_Count"] < summary["Chore_Count"]]

if len(needs_attention) == 0:
    message += "• Everyone is done 🎉\n"
else:
    for _, row in needs_attention.iterrows():
        message += f"• {row['Name']} ({row['Completed_Count']}/{row['Chore_Count']})\n"

# Top performers
message += "\n🏆 *Top Performers*\n"
top = summary[summary["Completed_Count"] == summary["Chore_Count"]]

if len(top) == 0:
    message += "• None yet\n"
else:
    for _, row in top.iterrows():
        message += f"• {row['Name']} ✅\n"

# --- SEND TO SLACK ---
client = WebClient(token=SLACK_TOKEN)

client.chat_postMessage(
    channel=SLACK_CHANNEL,
    text=message
)

print("✅ Report sent to Slack!")