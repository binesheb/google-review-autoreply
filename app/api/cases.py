from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AuditLog, Case
from app.security import require_admin

router = APIRouter(prefix="/api/cases", tags=["cases"])


class CaseIn(BaseModel):
    review_id: int
    category: str
    priority: str = "medium"
    owner: str | None = None
    due_at: datetime | None = None
    notes: str = ""


@router.get("")
def list_cases(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return db.scalars(select(Case).order_by(Case.created_at.desc()).limit(200)).all()


@router.post("")
def create_case(
    payload: CaseIn, db: Session = Depends(get_db), actor: str = Depends(require_admin)
):
    item = Case(
        review_id=payload.review_id,
        category=payload.category,
        priority=payload.priority,
        owner=payload.owner,
        due_at=payload.due_at,
        notes=payload.notes,
    )
    db.add(item)
    db.flush()
    db.add(
        AuditLog(
            action="case_created",
            actor=actor,
            target_type="case",
            target_id=str(item.id),
            detail=payload.category,
        )
    )
    db.commit()
    db.refresh(item)
    return item


@router.post("/{case_id}/close")
def close_case(case_id: int, db: Session = Depends(get_db), actor: str = Depends(require_admin)):
    item = db.get(Case, case_id)
    if not item:
        raise HTTPException(404, "Case not found")
    item.status = "closed"
    db.add(
        AuditLog(
            action="case_closed",
            actor=actor,
            target_type="case",
            target_id=str(item.id),
            detail="closed",
        )
    )
    db.commit()
    return {"id": item.id, "status": item.status}
