# clear_logs.py
import os

log_files = [
    "logs/standup_updates.jsonl",
    "logs/standup_summaries.md"
]

for path in ["logs/standup_updates.jsonl", "logs/standup_summaries.md"]:
    with open(path, "w") as f:
        f.write("")
print("✅ Log files emptied.")