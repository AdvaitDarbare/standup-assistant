import requests

def submit_standup():
    payload = {
        "@message": "standup_update",
        "user": input("Name: "),
        "yesterday": input("What did you do yesterday? "),
        "today": input("What will you do today? "),
        "blockers": input("Any blockers? ")
    }
    requests.post("http://localhost:3333/standup", json=payload)
    print("✅ Submitted!")

if __name__ == "__main__":
    submit_standup()