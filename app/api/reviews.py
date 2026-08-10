from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.service import ResponseService
from app.core.config import settings
from app.db import get_db
from app.google.client import GoogleBusinessProfileClient
from app.models import Approval, AuditLog, Location, OwnerReply, Review, ReviewVersion
from app.security import require_admin

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


class ReviewIn(BaseModel):
    source: str = "google"
    source_name: str
    source_review_id: str
    location_name: str
    reviewer_name: str | None = None
    rating: int
    comment: str = ""
    review_created_at: datetime | None = None
    review_updated_at: datetime | None = None
    has_owner_reply: bool = False


class DraftRequest(BaseModel):
    review_id: int


class ActionRequest(BaseModel):
    comment: str = ""


def _get_review(db: Session, review_id: int):
    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    return review


@router.get("")
def list_reviews(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    reviews = db.scalars(select(Review).order_by(Review.updated_at.desc()).limit(200)).all()
    return [
        {
            "id": r.id,
            "location": r.location.display_name,
            "rating": r.rating,
            "reviewer_name": r.reviewer_name,
            "status": r.status,
            "risk_level": r.risk_level,
            "comment": r.comment,
            "has_owner_reply": r.has_owner_reply,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        }
        for r in reviews
    ]


@router.post("/ingest", response_model=dict)
def ingest_review(
    payload: ReviewIn, db: Session = Depends(get_db), actor: str = Depends(require_admin)
):
    location = db.scalar(select(Location).where(Location.display_name == payload.location_name))
    if not location:
        raise HTTPException(404, "Location must be configured before review ingestion")

    review = db.scalar(select(Review).where(Review.source_name == payload.source_name))
    if not review:
        review = Review(
            source=payload.source,
            source_name=payload.source_name,
            source_review_id=payload.source_review_id,
            location_id=location.id,
            reviewer_name=payload.reviewer_name,
            rating=payload.rating,
            comment=payload.comment,
            review_created_at=payload.review_created_at,
            review_updated_at=payload.review_updated_at,
            has_owner_reply=payload.has_owner_reply,
            status="already_responded" if payload.has_owner_reply else "queued",
        )
        db.add(review)
        db.flush()
        db.add(
            ReviewVersion(
                review_id=review.id,
                version=1,
                rating=review.rating,
                comment=review.comment,
                has_owner_reply=review.has_owner_reply,
            )
        )
    else:
        changed = (
            review.rating != payload.rating
            or review.comment != payload.comment
            or review.has_owner_reply != payload.has_owner_reply
        )
        if changed:
            latest = db.scalar(
                select(ReviewVersion)
                .where(ReviewVersion.review_id == review.id)
                .order_by(ReviewVersion.version.desc())
            )
            version = (latest.version if latest else 0) + 1
            db.add(
                ReviewVersion(
                    review_id=review.id,
                    version=version,
                    rating=payload.rating,
                    comment=payload.comment,
                    has_owner_reply=payload.has_owner_reply,
                )
            )
        review.rating = payload.rating
        review.comment = payload.comment
        review.review_updated_at = payload.review_updated_at
        review.has_owner_reply = payload.has_owner_reply
        review.status = (
            "already_responded"
            if payload.has_owner_reply
            else ("queued" if review.status == "already_responded" else review.status)
        )

    db.add(
        AuditLog(
            action="review_ingested",
            actor=actor,
            target_type="review",
            target_id=payload.source_review_id,
            detail=payload.source_name,
        )
    )
    db.commit()
    db.refresh(review)
    return {"id": review.id, "status": review.status}


@router.post("/draft")
def draft(payload: DraftRequest, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    review = _get_review(db, payload.review_id)
    if review.has_owner_reply:
        raise HTTPException(409, "Review already has an owner reply")
    generated = ResponseService(db).draft(review)
    review.status = "approval_required" if not generated.auto_eligible else "auto_eligible"
    db.commit()
    return {
        "review_id": review.id,
        "draft_id": generated.id,
        "response": generated.response_text,
        "safety_passed": generated.safety_passed,
        "auto_eligible": generated.auto_eligible,
        "reasons": [x for x in generated.risk_reasons.split(";") if x],
        "evidence": generated.evidence,
    }


@router.post("/{review_id}/approve")
def approve(
    review_id: int,
    payload: ActionRequest,
    db: Session = Depends(get_db),
    actor: str = Depends(require_admin),
):
    review = _get_review(db, review_id)
    latest = review.drafts[-1] if review.drafts else None
    if not latest:
        raise HTTPException(409, "No AI draft exists")
    if not latest.safety_passed:
        raise HTTPException(409, "Safety gate failed")
    db.add(
        Approval(
            review_id=review.id,
            draft_id=latest.id,
            action="approve",
            actor=actor,
            comment=payload.comment,
        )
    )
    review.status = "approved"
    db.add(
        AuditLog(
            action="review_approved",
            actor=actor,
            target_type="review",
            target_id=str(review.id),
            detail=payload.comment,
        )
    )
    db.commit()
    return {"status": "approved", "review_id": review.id}


@router.post("/{review_id}/publish")
def publish(
    review_id: int,
    payload: ActionRequest,
    db: Session = Depends(get_db),
    actor: str = Depends(require_admin),
):
    review = _get_review(db, review_id)
    if not settings.google_enabled or not settings.google_access_token:
        raise HTTPException(503, "Google publishing is not configured")
    if review.has_owner_reply:
        raise HTTPException(409, "Review already has an owner reply")
    latest = review.drafts[-1] if review.drafts else None
    if not latest or not latest.safety_passed:
        raise HTTPException(409, "No safe draft available")
    approved = db.scalar(
        select(Approval)
        .where(Approval.review_id == review.id, Approval.action == "approve")
        .order_by(Approval.created_at.desc())
    )
    if not approved and not (
        settings.auto_publish_enabled and latest.auto_eligible and not settings.automation_paused
    ):
        raise HTTPException(403, "Approval is required before publishing")
    result = GoogleBusinessProfileClient(settings.google_access_token).update_reply(
        review.source_name, latest.response_text
    )
    review.has_owner_reply = True
    review.status = "published"
    db.add(OwnerReply(review_id=review.id, response_text=latest.response_text, actor=actor))
    db.add(
        AuditLog(
            action="owner_reply_published",
            actor=actor,
            target_type="review",
            target_id=str(review.id),
            detail=payload.comment,
        )
    )
    db.commit()
    return {"status": "published", "google": result}
