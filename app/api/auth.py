from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

from app.core.config import settings
from app.security import verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.get("/status")
def auth_status(request: Request):
    user = request.cookies.get("rip_user")
    return {"authenticated": bool(user and user == settings.admin_username), "username": user}


@router.post("/login")
def login(payload: LoginRequest, response: Response):
    if payload.username != settings.admin_username or not verify_password(
        payload.password, settings.admin_password_hash
    ):
        return Response(
            content='{"detail":"Invalid credentials"}',
            media_type="application/json",
            status_code=401,
        )
    response.set_cookie(
        "rip_user", payload.username, httponly=True, samesite="lax", secure=False, max_age=8 * 3600
    )
    return {"authenticated": True, "username": payload.username}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("rip_user")
    return {"authenticated": False}
