import json
from sseclient import SSEClient
from agent.summarizer import handle_standup

def main():
    # Open a persistent connection to the SSE endpoint
    messages = SSEClient("http://localhost:3333/standup")
    for msg in messages:
        if not msg.data:
            continue
        # Parse the JSON safely
        try:
            event = json.loads(msg.data)
        except json.JSONDecodeError:
            continue

        # Only handle actual standup updates
        if event.get("@message") == "standup_update":
            handle_standup(event)

if __name__ == "__main__":
    main()