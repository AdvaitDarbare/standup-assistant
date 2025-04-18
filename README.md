📋 Real-Time Standup Assistant

A real-time, agent-powered standup reporting system built with:
	•	🧠 OpenAI LLM (or any LLM)
	•	🛰 Server-Sent Events (SSE)
	•	🧩 Message-Channel Protocol (MCP)-style event flow
	•	🐍 Python (FastAPI + CLI agent)

⸻

🧠 Overview

This project lets teams submit asynchronous standup updates (yesterday/today/blockers). These updates stream to all subscribers in real time, are summarized by an AI agent, and the summary is broadcast back.

No meetings. No refresh buttons. Just clean, agentic, real-time collaboration.

⸻

⚙️ How It Works

🔁 The Flow

[User] --> POST /standup --> [FastAPI Server]
                                |
                                v
                        GET /standup (SSE)
                                |
                            [Agent]
                          |   |   |
      +----- Summary via OpenAI   |
      |                           |
[POST Summary] <------------------+
                                |
                            [SSE Stream Output]

🧩 Message Types (MCP-Inspired)
	•	@message: standup_update — when a user submits their status
	•	@message: standup_summary — when the agent summarizes them

These are sent to a common channel /standup.

⸻

📁 File Structure

standup-assistant/
├── agent/
│   ├── listener.py         # Listens to updates
│   └── summarizer.py       # Buffers + sends to LLM + emits summary
├── client/
│   └── submit.py           # CLI tool to submit standup
├── server.py               # FastAPI + SSE-based channel
├── .env                    # OpenAI API key
├── requirements.txt        # Dependencies
└── README.md               # You're reading it!



⸻

🛠 Setup

# Clone and enter project
cd standup-assistant

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo "OPENAI_API_KEY=sk-..." > .env



⸻

🚀 Run the System

1. Run the server

python3 -m uvicorn server:app --port 3333

2. Run the agent

python -m agent.listener

3. Submit standups

Run 3 times to trigger summary:

python client/submit.py

4. (Optional) Watch live stream

curl http://localhost:3333/standup



⸻

🧠 agent/summarizer.py (Core Logic)

buffer = []

# On receiving an event
buffer.append(event)

if len(buffer) >= 3:
    prompt = build_summary_prompt(buffer)
    summary = call_openai(prompt)

    requests.post("http://localhost:3333/standup", json={
        "@message": "standup_summary",
        "summary": summary
    })
    buffer.clear()

This simulates an MCP agent: reactive, stateless, and communicative.

⸻

✅ MCP Compatibility

MCP Concept	This Project Does It?
Channels	✅ /standup via FastAPI
@message/event	✅ standup_update + standup_summary
SSE (Streaming)	✅ Real-time via SSE
Agent model	✅ LLM listens + responds



⸻

🔮 Ideas to Extend
	•	🔔 Slack notifications
	•	💾 Save summaries to SQLite or Markdown
	•	🧠 Use local LLM via Ollama (Llama 3)
	•	📊 React or Streamlit dashboard for team
	•	🧪 Blocker analysis and trends

⸻

💬 Summary

This is a real-world, real-time MCP-style AI agent app:
	•	Built with simple Python tools
	•	Agent reacts to live streams
	•	Summarizes, posts back, and completes the loop

You’re ready to scale this to a full agentic system 🔥