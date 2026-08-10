from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AuditLog, InstructionSet, Organization
from app.security import require_admin

router = APIRouter(prefix="/api/instructions", tags=["instructions"])


class InstructionInput(BaseModel):
    content: str
    version: str


@router.get("")
def list_instructions(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return db.scalars(
        select(InstructionSet).order_by(InstructionSet.created_at.desc()).limit(50)
    ).all()


@router.post("")
def create_instruction(
    payload: InstructionInput, db: Session = Depends(get_db), actor: str = Depends(require_admin)
):
    org = db.scalar(select(Organization).order_by(Organization.id.asc()))
    if not org:
        raise HTTPException(409, "Configure the organisation first")
    db.query(InstructionSet).filter(
        InstructionSet.organization_id == org.id, InstructionSet.status == "active"
    ).update({"status": "archived"})
    item = InstructionSet(
        organization_id=org.id,
        version=payload.version,
        content=payload.content,
        status="active",
        created_by=actor,
    )
    db.add(item)
    db.flush()
    db.add(
        AuditLog(
            action="instructions_published",
            actor=actor,
            target_type="instructions",
            target_id=str(item.id),
            detail=payload.version,
        )
    )
    db.commit()
    db.refresh(item)
    return item
