from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("")
def get_settings():
    return {
        "environment": settings.app_env,
        "google_enabled": settings.google_enabled,
        "auto_publish_enabled": settings.auto_publish_enabled,
        "poll_interval_minutes": settings.poll_interval_minutes,
        "daily_publish_limit": settings.daily_publish_limit,
        "ai_base_url": settings.ai_base_url,
        "ai_model": settings.ai_model,
    }
