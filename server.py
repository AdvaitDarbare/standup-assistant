from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import asyncio
import uvicorn
import os
from dotenv import load_dotenv
import time
from datetime import datetime
import json

load_dotenv()

app = FastAPI()
# In-memory SSE buffer
events = []

# Chroma + Embedding setup
chroma = PersistentClient(path="chroma_data")
collection = chroma.get_or_create_collection("standup_memory")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submit")
async def submit_standup(request: Request):
    data = await request.json()
    # 1. Generate UTC timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    # 2. Build document ID and text
    doc_id = f"{data['user']}-{int(time.time())}"
    document = (
        f"[{timestamp}] {data['user']} – Yesterday: {data['yesterday']}; "
        f"Today: {data['today']}; Blockers: {data['blockers']}"
    )
    # 3. Embed and store
    embedding = embedder.encode(document).tolist()
    collection.add(
        documents=[document],
        embeddings=[embedding],
        ids=[doc_id],
        metadatas=[{"timestamp": timestamp, "user": data['user']}]
    )
    print("✅ Saved to Chroma:", document)

    # 4. Emit SSE event
    event = {
        "@message": "standup_update",
        "user": data['user'],
        "yesterday": data['yesterday'],
        "today": data['today'],
        "blockers": data['blockers'],
        "timestamp": timestamp
    }
    events.append(event)
    return {"status": "ok"}

@app.get("/standup")
async def stream_events():
    async def event_generator():
        last_idx = 0
        while True:
            await asyncio.sleep(1)
            for e in events[last_idx:]:
                yield f"data: {json.dumps(e)}\n\n"
            last_idx = len(events)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/slack/query")
async def handle_slack_query(text: str = Form(...)):
    # Simple semantic search against all stored docs
    query_embedding = embedder.encode(text).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=5)
    matches = results.get('documents', [[]])[0]

    if not matches:
        return PlainTextResponse("❌ No relevant standup updates found.")

    # Let LLM stitch the best hits into an answer
    prompt = (
        "You are answering a question using the following standup updates:\n\n"
        + "\n".join(f"- {m}" for m in matches)
        + f"\n\nQuestion: \"{text}\"\nAnswer precisely:"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content.strip()
    return PlainTextResponse(f"*Answer:* {answer}")

if __name__ == "__main__":
    uvicorn.run(app, port=3333)