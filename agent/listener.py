from sseclient import SSEClient
from agent.summarizer import handle_standup

def main():
    messages = SSEClient("http://localhost:3333/standup")
    for msg in messages:
        if msg.data and "standup_update" in msg.data:
            handle_standup(eval(msg.data))  # quick hack for demo

if __name__ == "__main__":
    main()