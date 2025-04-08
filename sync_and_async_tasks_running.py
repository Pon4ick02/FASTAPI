from fastapi import FastAPI, BackgroundTasks
import time
import asyncio
import uvicorn


app = FastAPI()

def sync_task():
    print("Sync task started")
    time.sleep(2)
    print("Sync task finished")

async def async_task():
    await asyncio.sleep(3)
    print("Async task finished")
    


@app.post('/')
async def some_route(bg: BackgroundTasks):
    bg.add_task(sync_task)
    bg.add_task(async_task)
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
