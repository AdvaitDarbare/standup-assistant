from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()
events = []

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