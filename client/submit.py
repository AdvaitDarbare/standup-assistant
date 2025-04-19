import requests

def submit_standup():
    payload = {
        "user":      input("Name: "),
        "yesterday": input("What did you do yesterday? "),
        "today":     input("What will you do today? "),
        "blockers":  input("Any blockers? "),
    }
    resp = requests.post("http://localhost:3333/submit", json=payload)
    if resp.ok:
        print("✅ Submitted! Server stored with timestamp.")
    else:
        print("❌ Submission failed:", resp.text)

if __name__ == "__main__":
    submit_standup()