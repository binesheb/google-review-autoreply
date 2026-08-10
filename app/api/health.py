from fastapi import APIRouter
from sqlalchemy import text
from app.db import engine
from app.core.config import settings

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def health():
    database = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        database = f"error: {exc.__class__.__name__}"
    return {
        "status": "ok" if database == "ok" else "degraded",
        "product": settings.app_name,
        "database": database,
        "google_enabled": settings.google_enabled,
        "auto_publish_enabled": settings.auto_publish_enabled,
        "automation_paused": settings.automation_paused,
        "ai_model": settings.ai_model,
        "environment": settings.app_env,
    }
