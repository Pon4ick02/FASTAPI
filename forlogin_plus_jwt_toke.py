from fastapi import FastAPI, Depends, HTTPException, Response
from authx import AuthX, AuthXConfig
from pydantic import BaseModel
import uvicorn
app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ['cookies']

security = AuthX(config)

class UserLoginSchema(BaseModel):
    username: str
    password: str

@app.post('/login')
async def login(creds: UserLoginSchema, response: Response):
    if creds.username == "admin" and creds.password == "admin":
        token = security.create_access_token(uid="12345")
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {"access_token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/protected", dependencies=[Depends(security.access_token_required)])
async def protected():
    return {"message": "You are authorized and you are top secret man"}



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
