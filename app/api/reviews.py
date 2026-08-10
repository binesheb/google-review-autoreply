from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Review, Location, Approval, AuditLog
from app.schemas import ReviewIn, DraftRequest, DraftResponse, ActionRequest
from app.ai.service import ResponseService
from app.core.config import settings
from app.google.client import GoogleBusinessProfileClient

router = APIRouter(prefix="/api/reviews", tags=["reviews"])

def _get_review(db: Session, review_id: int):
    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    return review

@router.get("")
def list_reviews(db: Session = Depends(get_db)):
    return db.scalars(select(Review).order_by(Review.updated_at.desc()).limit(200)).all()

@router.post("/ingest", response_model=dict)
def ingest_review(payload: ReviewIn, db: Session = Depends(get_db)):
    location = db.scalar(select(Location).where(Location.google_name == payload.location_name))
    if not location:
        location = Location(google_name=payload.location_name, display_name=payload.location_name)
        db.add(location); db.flush()
    review = db.scalar(select(Review).where(Review.google_name == payload.google_name))
    if not review:
        review = Review(google_name=payload.google_name, google_review_id=payload.google_review_id,
                        location_id=location.id, reviewer_name=payload.reviewer_name, rating=payload.rating,
                        comment=payload.comment, review_created_at=payload.review_created_at,
                        review_updated_at=payload.review_updated_at, has_google_reply=payload.has_google_reply,
                        status="already_responded" if payload.has_google_reply else "queued")
        db.add(review)
    else:
        review.rating = payload.rating
        review.comment = payload.comment
        review.has_google_reply = payload.has_google_reply
        if payload.has_google_reply:
            review.status = "already_responded"
    db.add(AuditLog(action="review_ingested", target_type="review", target_id=payload.google_review_id, detail=payload.google_name))
    db.commit(); db.refresh(review)
    return {"id": review.id, "status": review.status}

@router.post("/draft", response_model=DraftResponse)
def draft(payload: DraftRequest, db: Session = Depends(get_db)):
    review = _get_review(db, payload.review_id)
    if review.has_google_reply:
        raise HTTPException(409, "Review already has a Google reply")
    draft = ResponseService(db).draft(review)
    review.status = "approval_required" if not draft.auto_eligible else "auto_eligible"
    db.commit()
    return DraftResponse(review_id=review.id, draft_id=draft.id, response=draft.response_text,
                         safety_passed=draft.safety_passed, auto_eligible=draft.auto_eligible,
                         reasons=[x for x in draft.risk_reasons.split(";") if x])

@router.post("/{review_id}/approve")
def approve(review_id: int, payload: ActionRequest, db: Session = Depends(get_db)):
    review = _get_review(db, review_id)
    latest = review.drafts[-1] if review.drafts else None
    if not latest:
        raise HTTPException(409, "No AI draft exists")
    if not latest.safety_passed:
        raise HTTPException(409, "Safety gate failed")
    db.add(Approval(review_id=review.id, action="approve", actor=payload.actor, comment=payload.comment))
    review.status = "approved"
    db.add(AuditLog(action="review_approved", target_type="review", target_id=str(review.id), detail=payload.actor))
    db.commit()
    return {"status": "approved", "review_id": review.id}

@router.post("/{review_id}/publish")
def publish(review_id: int, payload: ActionRequest, db: Session = Depends(get_db)):
    review = _get_review(db, review_id)
    if not settings.google_enabled or not settings.google_access_token:
        raise HTTPException(503, "Google publishing is not configured")
    if review.has_google_reply:
        raise HTTPException(409, "Review already has a Google reply")
    latest = review.drafts[-1] if review.drafts else None
    if not latest or not latest.safety_passed:
        raise HTTPException(409, "No safe draft available")
    approved = db.scalar(select(Approval).where(Approval.review_id == review.id, Approval.action == "approve").order_by(Approval.created_at.desc()))
    if not approved:
        raise HTTPException(403, "Human approval is required before publishing")
    result = GoogleBusinessProfileClient(settings.google_access_token).update_reply(review.google_name, latest.response_text)
    review.has_google_reply = True
    review.status = "published"
    db.add(AuditLog(action="google_reply_published", target_type="review", target_id=str(review.id), detail=payload.actor))
    db.commit()
    return {"status": "published", "google": result}
