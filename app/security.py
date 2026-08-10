import hashlib
import hmac
import secrets

from fastapi import HTTPException, Request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings

SESSION_COOKIE = "rip_session"
SESSION_MAX_AGE = 8 * 3600


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


def _serializer() -> URLSafeTimedSerializer:
    if not settings.secret_key:
        raise RuntimeError("SECRET_KEY must be configured before authentication is used")
    return URLSafeTimedSerializer(settings.secret_key, salt="review-platform-session")


def create_session(username: str) -> str:
    return _serializer().dumps({"username": username})


def read_session(token: str | None) -> str | None:
    if not token:
        return None
    try:
        payload = _serializer().loads(token, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    username = payload.get("username")
    return username if isinstance(username, str) else None


def require_admin(request: Request) -> str:
    username = read_session(request.cookies.get(SESSION_COOKIE))
    if not username or username != settings.admin_username:
        raise HTTPException(status_code=401, detail="Authentication required")
    return username
