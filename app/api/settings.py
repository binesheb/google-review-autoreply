from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db import get_db
from app.models import SystemSetting, AuditLog

router = APIRouter(prefix="/api/settings", tags=["settings"])

class SettingUpdate(BaseModel):
    value: str
    actor: str = "dashboard"

@router.get("")
def get_settings(db: Session = Depends(get_db)):
    stored = {x.key: x.value for x in db.scalars(select(SystemSetting)).all()}
    return {
        "environment": settings.app_env,
        "google_enabled": settings.google_enabled,
        "auto_publish_enabled": stored.get("auto_publish_enabled", str(settings.auto_publish_enabled).lower()) == "true",
        "automation_paused": stored.get("automation_paused", "false") == "true",
        "poll_interval_minutes": int(stored.get("poll_interval_minutes", settings.poll_interval_minutes)),
        "daily_publish_limit": int(stored.get("daily_publish_limit", settings.daily_publish_limit)),
        "ai_base_url": settings.ai_base_url,
        "ai_model": settings.ai_model,
    }

@router.put("/{key}")
def update_setting(key: str, payload: SettingUpdate, db: Session = Depends(get_db)):
    allowed = {"auto_publish_enabled", "automation_paused", "poll_interval_minutes", "daily_publish_limit"}
    if key not in allowed:
        raise HTTPException(400, "Setting is not dashboard-editable")
    if key in {"auto_publish_enabled", "automation_paused"} and payload.value.lower() not in {"true", "false"}:
        raise HTTPException(400, "Boolean setting requires true or false")
    if key in {"poll_interval_minutes", "daily_publish_limit"}:
        try:
            if int(payload.value) <= 0: raise ValueError
        except ValueError:
            raise HTTPException(400, "Setting requires a positive integer")
    item = db.scalar(select(SystemSetting).where(SystemSetting.key == key))
    if not item:
        item = SystemSetting(key=key, value=payload.value, updated_by=payload.actor)
        db.add(item)
    else:
        item.value = payload.value; item.updated_by = payload.actor
    db.add(AuditLog(action="setting_changed", target_type="setting", target_id=key, detail=f"{payload.actor}:{payload.value}"))
    db.commit()
    return {"key": key, "value": payload.value}
