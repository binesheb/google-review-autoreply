from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.models import AuditLog, Location, Organization
from app.security import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


class OrganizationInput(BaseModel):
    name: str
    timezone: str = "UTC"


class LocationInput(BaseModel):
    display_name: str
    code: str | None = None
    google_name: str | None = None


@router.get("/bootstrap")
def bootstrap(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    org = db.scalar(select(Organization).order_by(Organization.id.asc()))
    return {
        "product": settings.app_name,
        "organization": None
        if not org
        else {"id": org.id, "name": org.name, "timezone": org.timezone},
        "locations": []
        if not org
        else [
            {
                "id": x.id,
                "display_name": x.display_name,
                "code": x.code,
                "google_name": x.google_name,
            }
            for x in org.locations
        ],
    }


@router.post("/organization")
def create_organization(
    payload: OrganizationInput, db: Session = Depends(get_db), actor: str = Depends(require_admin)
):
    org = db.scalar(select(Organization).order_by(Organization.id.asc()))
    if org:
        org.name = payload.name
        org.timezone = payload.timezone
    else:
        org = Organization(name=payload.name, timezone=payload.timezone)
        db.add(org)
        db.flush()
    db.add(
        AuditLog(
            action="organization_updated",
            actor=actor,
            target_type="organization",
            target_id=str(org.id),
            detail=org.name,
        )
    )
    db.commit()
    return {"id": org.id, "name": org.name, "timezone": org.timezone}


@router.post("/locations")
def create_location(
    payload: LocationInput, db: Session = Depends(get_db), actor: str = Depends(require_admin)
):
    org = db.scalar(select(Organization).order_by(Organization.id.asc()))
    if not org:
        org = Organization(name=settings.app_name, timezone=settings.app_timezone)
        db.add(org)
        db.flush()
    location = Location(
        organization_id=org.id,
        display_name=payload.display_name,
        code=payload.code,
        google_name=payload.google_name,
    )
    db.add(location)
    db.add(
        AuditLog(
            action="location_created",
            actor=actor,
            target_type="location",
            target_id=payload.display_name,
            detail=payload.google_name or "",
        )
    )
    db.commit()
    db.refresh(location)
    return {
        "id": location.id,
        "display_name": location.display_name,
        "code": location.code,
        "google_name": location.google_name,
    }
