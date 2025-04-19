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
import time  # ensure this is imported at the top if not already

load_dotenv()

app = FastAPI()
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
    doc_id = f"{data['user']}-{int(time.time())}"
    document = f"{data['user']} - Yesterday: {data['yesterday']}. Today: {data['today']}. Blockers: {data['blockers']}"
    embedding = embedder.encode(document).tolist()
    collection.add(documents=[document], embeddings=[embedding], ids=[doc_id])
    print("✅ Saved to Chroma:", document)
    return {"status": "saved to chroma"}

@app.post("/slack/query")
async def handle_slack_query(text: str = Form(...)):
    query_embedding = embedder.encode(text).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=5)
    matches = results['documents'][0] if results['documents'] else []

    if not matches:
        return PlainTextResponse("❌ No relevant standup updates found.")

    match_text = "\n".join([f"- {m}" for m in matches])
    prompt = f"""
        You are answering a question using the following standup updates.

        Standup Updates:
        {match_text}

        Question: "{text}"

        Be precise. List every person mentioned in the context who worked on the task, even if mentioned briefly.
        """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content.strip()
    return PlainTextResponse(f"*Answer:*{answer}")

@app.post("/standup")
async def receive_event(request: Request):
    data = await request.json()
    events.append(data)
    return {"status": "received"}

@app.get("/standup")
async def stream_events():
    async def event_generator():
        last_idx = 0
        while True:
            await asyncio.sleep(1)
            new = events[last_idx:]
            last_idx = len(events)
            for e in new:
                yield f"data: {e}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, port=3333)