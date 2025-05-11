from fastapi import FastAPI, BackgroundTasks
import time
import asyncio
import uvicorn

app = FastAPI()


def sync_task():
    print("🔧 Sync task started")
    time.sleep(2)  # Blocks the thread
    print("✅ Sync task finished")


async def async_task():
    print("⚙️ Async task started")
    await asyncio.sleep(3)  # Non-blocking
    print("✅ Async task finished")

@app.post("/")
async def some_route(bg: BackgroundTasks):
    """
    Endpoint that triggers background tasks (both sync and async).
    Responds immediately while tasks continue in the background.
    """
    bg.add_task(sync_task)    # Will run after response is returned
    bg.add_task(async_task)   # Allowed, but won't be awaited
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
