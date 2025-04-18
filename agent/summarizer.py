import os
import time
import threading
from openai import OpenAI
import requests
from dotenv import load_dotenv
import json
from datetime import datetime
from slack_sdk import WebClient

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

buffer = []

def handle_standup(event):
    global buffer
    print(f"📥 Received standup from {event['user']}")
    buffer.append(event)

    # ✅ Save each update immediately
    with open("logs/standup_updates.json", "a") as f:
        f.write(json.dumps(event) + "\n")

def summarize_every_30_seconds():
    global buffer

    while True:
        time.sleep(30)  # ⏱ Wait 30 seconds

        if buffer:
            print("⏰ 30 seconds passed. Generating summary...")

            updates = "\n".join(
                [f"{e['user']}:\nYesterday: {e['yesterday']}\nToday: {e['today']}\nBlockers: {e['blockers']}\n" for e in buffer]
            )

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{
                        "role": "user",
                        "content": f"Summarize this team's standup:\n\n{updates}"
                    }]
                )
                summary = response.choices[0].message.content.strip()
                print("🧠 Summary:\n", summary)

                # Post to FastAPI event stream
                requests.post("http://localhost:3333/standup", json={
                    "@message": "standup_summary",
                    "summary": summary
                })

                # 📝 Save Markdown summary
                with open("logs/standup_summaries.md", "a") as f:
                    f.write(f"\n## Summary ({datetime.now().strftime('%Y-%m-%d %H:%M')}):\n{summary}\n")

                # ✅ Post to Slack
                slack_token = os.getenv("SLACK_API_TOKEN")
                slack_channel = os.getenv("SLACK_CHANNEL", "#general")
                if slack_token:
                    slack_client = WebClient(token=slack_token)
                    slack_client.chat_postMessage(channel=slack_channel, text=f"*Daily Standup Summary:*\n{summary}")
                    print("✅ Posted to Slack!")
                else:
                    print("⚠️ SLACK_API_TOKEN not set. Skipping Slack post.")

                # Clear buffer after summary
                buffer.clear()

            except Exception as e:
                print(f"❌ Error summarizing or posting: {e}")

# Start background thread
threading.Thread(target=summarize_every_30_seconds, daemon=True).start()