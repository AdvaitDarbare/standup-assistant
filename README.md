# 🤖 Standup Assistant

A lightweight real-time standup bot that collects team updates via CLI, summarizes them using OpenAI, and posts the summary to Slack.

---

## 💡 Features

- Submit standup updates via terminal
- Server with event-streaming via FastAPI
- Auto-summarizes standups using OpenAI (every 30 seconds)
- Posts summary to Slack
- Logs raw updates and summaries to disk (`.jsonl` + `.md`)

---

## 🛠 Project Structure

```
standup-assistant/
├── agent/
│   ├── listener.py         # Listens to server events and handles summaries
│   └── summarizer.py       # OpenAI summarizer logic + Slack post
├── client/
│   └── submit.py           # CLI form to submit your standup
├── logs/
│   ├── standup_updates.jsonl  # All raw updates
│   └── standup_summaries.md   # All summaries
├── server.py              # FastAPI SSE server
├── .env                   # API keys (DO NOT COMMIT)
├── requirements.txt       # Python dependencies
└── README.md
```

---

## ⚙️ Setup

1. **Clone the repo**

```bash
git clone https://github.com/YOUR_USERNAME/standup-assistant.git
cd standup-assistant
```

2. **Create a virtual environment and install dependencies**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. **Add your secrets to `.env`**

```env
OPENAI_API_KEY=your-openai-key
SLACK_API_TOKEN=your-slack-bot-token
SLACK_CHANNEL=#standup-daily
```

4. **Run the FastAPI server**

```bash
python3 -m uvicorn server:app --port 3333
```

---

## 🚀 Usage

### 1. Start the summarizer listener
```bash
python -m agent.listener
```

This listens to new standups, appends them to a buffer, and every 30 seconds posts a summary if there’s anything to summarize.

---

### 2. Submit a standup from any team member
```bash
python client/submit.py
```

You'll be prompted:

```
Name: advait
What did you do yesterday? fixed bugs
What will you do today? code review
Any blockers? none
```

---

### 3. Slack Integration

After every 30 seconds (or customizable time), a formatted summary is posted to your configured Slack channel:

```
*Daily Standup Summary:*
Advait fixed bugs yesterday and is doing code review today. No blockers.
```

---

## 📝 Logs

- **Raw updates**: `logs/standup_updates.jsonl`
- **Summaries**: `logs/standup_summaries.md`

---

## 🔐 Secrets & Git

Make sure to add `.env` to your `.gitignore`:

```bash
echo ".env" >> .gitignore
```

Never commit secrets to GitHub! Use `.env.example` to share structure.

---

## 📦 Future Ideas

- Web dashboard to view all updates/summaries
- GitHub bot integration
- Voice-based daily check-in (via Twilio or WebRTC)
- Personalized reminders for users
- AI-generated blockers resolution suggestions

---

## 🤝 Contributions

Open to PRs! Feel free to fork and improve the summarization, Slack formatting, or add new features!

---

## 📄 License

MIT License.
