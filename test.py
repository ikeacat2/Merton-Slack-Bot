import os
from slack_sdk import WebClient

slack_token = os.getenv("SLACK_TOKEN")
if not slack_token:
    raise ValueError("SLACK_TOKEN environment variable not set")

client = WebClient(token=slack_token)

client.chat_postMessage(
    channel="#chores",
    text="👋 Chore bot is alive!"
)