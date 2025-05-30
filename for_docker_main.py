from fastapi import FastAPI
import uvicorn


app = FastAPI()

@app.get("/users")
async def get_users():
    return {"id": 1, "name": "John Doe"}

if __name__ == "__main__":
    uvicorn.run("for_docker_main:app", host="0.0.0.0", port=8000)
