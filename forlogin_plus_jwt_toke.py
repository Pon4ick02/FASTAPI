from fastapi import FastAPI, Depends, HTTPException, Response, status, Request, Cookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
from authx import AuthX, AuthXConfig
from passlib.context import CryptContext
import uvicorn
import logging

app = FastAPI(title="Advanced Auth Example", description="FastAPI Auth with Roles and Cookie-based JWT")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


fake_users_db = {
    "admin": {
        "id": "1",
        "username": "admin",
        "hashed_password": pwd_context.hash("admin"),
        "role": "admin"
    },
    "user": {
        "id": "2",
        "username": "user",
        "hashed_password": pwd_context.hash("user123"),
        "role": "user"
    }
}


config = AuthXConfig()
config.JWT_SECRET_KEY = "SUPER_SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_REFRESH_COOKIE_NAME = "refresh_token"
config.JWT_TOKEN_LOCATION = ['cookies']
config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15
config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

security = AuthX(config)



class UserLoginSchema(BaseModel):
    username: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class ProtectedData(BaseModel):
    message: str
    user_id: str
    role: str



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str):
    return fake_users_db.get(username)



@app.post('/login', response_model=TokenSchema)
async def login(creds: UserLoginSchema, response: Response):
    user = get_user(creds.username)
    if not user or not verify_password(creds.password, user["hashed_password"]):
        logger.warning(f"Failed login attempt for user: {creds.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = security.create_access_token(uid=user["id"], custom_claims={"role": user["role"]})
    refresh_token = security.create_refresh_token(uid=user["id"])

    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token, httponly=True)
    response.set_cookie(config.JWT_REFRESH_COOKIE_NAME, refresh_token, httponly=True)

    logger.info(f"User {creds.username} logged in successfully.")
    return {"access_token": access_token, "refresh_token": refresh_token}


@app.post("/refresh", response_model=TokenSchema)
async def refresh_token(request: Request, refresh_token: Optional[str] = Cookie(None), response: Response = None):
    if not refresh_token:
        raise HTTPException(status_code=403, detail="Refresh token missing")

    try:
        payload = security.decode_refresh_token(refresh_token)
        user_id = payload["sub"]
        role = payload.get("role", "user")

        new_access_token = security.create_access_token(uid=user_id, custom_claims={"role": role})
        new_refresh_token = security.create_refresh_token(uid=user_id)

        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, new_access_token, httponly=True)
        response.set_cookie(config.JWT_REFRESH_COOKIE_NAME, new_refresh_token, httponly=True)

        return {"access_token": new_access_token, "refresh_token": new_refresh_token}
    except Exception as e:
        logger.error(f"Refresh failed: {e}")
        raise HTTPException(status_code=403, detail="Invalid refresh token")


@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(config.JWT_REFRESH_COOKIE_NAME)
    return {"message": "Logged out"}



@app.get("/protected", response_model=ProtectedData)
async def protected(user_data=Depends(security.access_token_required)):
    uid = user_data.get("sub")
    role = user_data.get("role", "unknown")
    return {"message": "Welcome to the secret zone!", "user_id": uid, "role": role}


@app.get("/admin")
async def admin_only(user_data=Depends(security.access_token_required)):
    if user_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admins only!")
    return {"message": "Welcome Admin!"}



@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
