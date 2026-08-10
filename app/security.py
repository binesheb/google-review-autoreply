import hashlib
import hmac
import secrets

from fastapi import HTTPException, Request

from app.core.config import settings


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 210_000)
    return f"pbkdf2_sha256$210000${salt}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        _, iterations, salt, expected = encoded.split("$", 3)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
        return hmac.compare_digest(digest.hex(), expected)
    except (ValueError, TypeError):
        return False


def require_admin(request: Request) -> str:
    username = request.cookies.get("rip_user")
    if not username or username != settings.admin_username:
        raise HTTPException(status_code=401, detail="Authentication required")
    return username
