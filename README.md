# 🤖 Standup Assistant

A real-time standup bot powered by OpenAI, ChromaDB, and Slack. Collects team updates via CLI or API, stores them in vector memory, auto-summarizes them, and enables querying via Slack.

---

## 💡 Features

- Submit standup updates via CLI or API
- Store structured updates in ChromaDB (vector DB)
- Auto-summarize using OpenAI every 60s
- Slack bot integration for posting summaries
- Slack slash command (`/standup-query`) to query standup memory
- View live streaming summaries via FastAPI SSE
- Streamlit dashboard to group standups by date
- Logs raw updates and summaries to disk (`.jsonl`, `.md`)

---

## 🛠 Project Structure

```
standup-assistant/
├── agent/
│   ├── listener.py           # Background summarizer + Slack post
├── client/
│   └── submit.py             # CLI form to submit standups
├── logs/
│   ├── standup_updates.jsonl
│   └── standup_summaries.md
├── chroma.py                 # Inspect ChromaDB contents
├── query_agent.py            # CLI: Query vector memory
├── server.py                 # FastAPI server + Slack command endpoint
├── dashboard.py              # Streamlit dashboard UI
├── .env                      # API keys (DO NOT COMMIT)
├── requirements.txt          # Python dependencies
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

5. **(Optional) Start ngrok for Slack external access**
```bash
ngrok http 3333
```

Copy the forwarding URL into your Slack slash command config.

---

## 🚀 Usage

### 1. Start the summarizer listener
```bash
python3 -m agent.listener
```

This listens to new standups and summarizes every 60 seconds.

---

### 2. Submit a standup
```bash
python3 client/submit.py
```

You’ll be prompted to enter:
```
Name: advait
What did you do yesterday? fixed bugs
What will you do today? code review
Any blockers? none
```

---

### 3. Query from Slack

In Slack:
```bash
/standup-query who worked on sql?
```

You’ll get an AI-generated answer from standup memory.

---

## 📊 Logs & Vector Memory

- `logs/standup_updates.jsonl` — raw submissions
- `logs/standup_summaries.md` — markdown summaries
- `chroma_data/` — vector store via ChromaDB

---

## 🔐 Secrets & Git

Make sure `.env` is in `.gitignore`:
```bash
echo ".env" >> .gitignore
```

---

## 🧠 Future Enhancements

- Web dashboard (✅ done)
- Llama3 support via Ollama
- Slack thread responses
- LangGraph memory flows
- Slack DMs to collect check-ins
- Query analytics and trends

---

## 🤝 Contributions

Open to PRs! Add a new feature, LLM model, or integration!

---

## 📄 License

MIT License
