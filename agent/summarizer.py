import os
import time
import threading
import json
from datetime import datetime
from openai import OpenAI
import requests
from dotenv import load_dotenv
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from slack_sdk import WebClient

load_dotenv()

# OpenAI + Chroma + embedder
client   = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma   = PersistentClient(path="chroma_data")
collection = chroma.get_or_create_collection("standup_memory")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# In‑memory buffer of incoming events
buffer = []

def handle_standup(event):
    global buffer
    # Ensure we have a timestamp
    ts = event.get("timestamp") or datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    event["timestamp"] = ts

    print(f"📥 Received standup from {event['user']} at {ts}")
    buffer.append(event)

    # 1) Append to raw‑log JSONL
    with open("logs/standup_updates.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")

    # 2) Store into Chroma with metadata
    doc_id   = f"{event['user']}-{int(time.time())}"
    document = (
        f"[{ts}] {event['user']} – Yesterday: {event['yesterday']}; "
        f"Today: {event['today']}; Blockers: {event['blockers']}"
    )
    embedding = embedder.encode(document).tolist()
    collection.add(
        documents=[document],
        embeddings=[embedding],
        ids=[doc_id],
        metadatas=[{"timestamp": ts}],
    )
    print("✅ Added to Chroma:", document)

# Background summarizer runs every 60 seconds
def summarize_every_60_seconds():
    global buffer
    while True:
        time.sleep(60)
        if not buffer:
            continue

        # Build the prompt
        updates = "\n".join(
            f"[{e['timestamp']}] {e['user']}: Yesterday: {e['yesterday']} | Today: {e['today']} | Blockers: {e['blockers']}"
            for e in buffer
        )

        try:
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Summarize this team's standup:\n\n{updates}"}],
            )
            summary = resp.choices[0].message.content.strip()
            print("🧠 Summary:\n", summary)

            # 3) Emit summary into SSE stream
            requests.post("http://localhost:3333/standup", json={
                "@message": "standup_summary",
                "summary": summary,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            })

            # 4) Append to Markdown log
            with open("logs/standup_summaries.md", "a") as f:
                f.write(f"\n## Summary ({datetime.utcnow().strftime('%Y-%m-%d %H:%M')}):\n{summary}\n")

            # 5) Post to Slack
            slack_token   = os.getenv("SLACK_API_TOKEN")
            slack_channel = os.getenv("SLACK_CHANNEL", "#general")
            if slack_token:
                WebClient(token=slack_token).chat_postMessage(
                    channel=slack_channel,
                    text=f"*Daily Standup Summary:*\n{summary}"
                )
                print("✅ Posted to Slack!")
        except Exception as e:
            print("❌ Error summarizing:", e)
        finally:
            buffer.clear()

# Kick off the background thread on import
threading.Thread(target=summarize_every_60_seconds, daemon=True).start()