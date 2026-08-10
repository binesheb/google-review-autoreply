from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import KnowledgeItem, AuditLog

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

class KnowledgeIn(BaseModel):
    title: str
    content: str
    scope: str = "company"
    status: str = "draft"
    source: str = "dashboard"
    expires_at: datetime | None = None
    actor: str = "dashboard"

@router.get("")
def list_knowledge(db: Session = Depends(get_db)):
    return db.scalars(select(KnowledgeItem).order_by(KnowledgeItem.updated_at.desc())).all()

@router.post("")
def create_knowledge(payload: KnowledgeIn, db: Session = Depends(get_db)):
    if payload.status not in {"draft", "pending_verification", "verified", "active", "expired", "archived"}:
        raise HTTPException(400, "Invalid knowledge status")
    item = KnowledgeItem(title=payload.title, content=payload.content, scope=payload.scope,
                         status=payload.status, source=payload.source, expires_at=payload.expires_at)
    db.add(item); db.flush()
    db.add(AuditLog(action="knowledge_created", target_type="knowledge", target_id=str(item.id), detail=payload.actor))
    db.commit(); db.refresh(item)
    return item

@router.put("/{item_id}")
def update_knowledge(item_id: int, payload: KnowledgeIn, db: Session = Depends(get_db)):
    item = db.get(KnowledgeItem, item_id)
    if not item: raise HTTPException(404, "Knowledge item not found")
    item.title = payload.title; item.content = payload.content; item.scope = payload.scope
    item.status = payload.status; item.source = payload.source; item.expires_at = payload.expires_at
    db.add(AuditLog(action="knowledge_updated", target_type="knowledge", target_id=str(item.id), detail=payload.actor))
    db.commit(); db.refresh(item)
    return item
