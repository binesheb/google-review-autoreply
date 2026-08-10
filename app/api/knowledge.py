from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AuditLog, KnowledgeItem, Organization
from app.security import require_admin

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class KnowledgeIn(BaseModel):
    title: str
    content: str
    scope: str = "organization"
    status: str = "draft"
    source: str = "dashboard"
    expires_at: datetime | None = None


@router.get("")
def list_knowledge(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return db.scalars(select(KnowledgeItem).order_by(KnowledgeItem.updated_at.desc())).all()


@router.post("")
def create_knowledge(
    payload: KnowledgeIn, db: Session = Depends(get_db), actor: str = Depends(require_admin)
):
    if payload.status not in {
        "draft",
        "pending_verification",
        "verified",
        "active",
        "expired",
        "archived",
    }:
        raise HTTPException(400, "Invalid knowledge status")
    org = db.scalar(select(Organization).order_by(Organization.id.asc()))
    if not org:
        raise HTTPException(409, "Configure the organisation first")
    item = KnowledgeItem(
        organization_id=org.id,
        title=payload.title,
        content=payload.content,
        scope=payload.scope,
        status=payload.status,
        source=payload.source,
        expires_at=payload.expires_at,
        verified_by=actor if payload.status == "verified" else None,
    )
    db.add(item)
    db.flush()
    db.add(
        AuditLog(
            action="knowledge_created",
            actor=actor,
            target_type="knowledge",
            target_id=str(item.id),
            detail=payload.title,
        )
    )
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}")
def update_knowledge(
    item_id: int,
    payload: KnowledgeIn,
    db: Session = Depends(get_db),
    actor: str = Depends(require_admin),
):
    item = db.get(KnowledgeItem, item_id)
    if not item:
        raise HTTPException(404, "Knowledge item not found")
    item.title = payload.title
    item.content = payload.content
    item.scope = payload.scope
    item.status = payload.status
    item.source = payload.source
    item.expires_at = payload.expires_at
    if payload.status == "verified":
        item.verified_by = actor
    db.add(
        AuditLog(
            action="knowledge_updated",
            actor=actor,
            target_type="knowledge",
            target_id=str(item.id),
            detail=payload.title,
        )
    )
    db.commit()
    db.refresh(item)
    return item
