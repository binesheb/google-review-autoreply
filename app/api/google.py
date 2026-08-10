from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.core.config import settings
from app.db import SessionLocal
from app.google.client import GoogleBusinessProfileClient
from app.models import AuditLog, Location, Review, ReviewVersion
from app.security import require_admin

router = APIRouter(prefix="/api/google", tags=["google"])
RATING_MAP = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}


def _parse_time(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@router.post("/sync")
def sync_reviews(actor: str = Depends(require_admin)):
    if not settings.google_enabled or not settings.google_access_token:
        raise HTTPException(503, "Google integration is not configured")
    db = SessionLocal()
    imported = 0
    pages = 0
    try:
        client = GoogleBusinessProfileClient(settings.google_access_token)
        locations = db.scalars(select(Location).where(Location.enabled == True)).all()  # noqa: E712
        for location in locations:
            if not location.google_name:
                continue
            token = None
            while True:
                data = client.list_reviews(location.google_name, token, 50)
                pages += 1
                for item in data.get("reviews", []):
                    reviewer = item.get("reviewer") or {}
                    reply = item.get("reviewReply")
                    name = item.get("name")
                    existing = db.scalar(select(Review).where(Review.source_name == name))
                    rating = RATING_MAP.get(item.get("starRating"), 0)
                    comment = item.get("comment", "")
                    has_reply = bool(reply)
                    if not existing:
                        existing = Review(
                            source="google", source_name=name, source_review_id=item.get("reviewId", ""), location_id=location.id,
                            reviewer_name=reviewer.get("displayName"), rating=rating, comment=comment,
                            review_created_at=_parse_time(item.get("createTime")), review_updated_at=_parse_time(item.get("updateTime")),
                            has_owner_reply=has_reply, status="already_responded" if has_reply else "queued")
                        db.add(existing)
                        db.flush()
                        db.add(ReviewVersion(review_id=existing.id, version=1, rating=rating, comment=comment, has_owner_reply=has_reply))
                        imported += 1
                    else:
                        changed = existing.rating != rating or existing.comment != comment or existing.has_owner_reply != has_reply
                        if changed:
                            latest = db.scalar(select(ReviewVersion).where(ReviewVersion.review_id == existing.id).order_by(ReviewVersion.version.desc()))
                            db.add(ReviewVersion(review_id=existing.id, version=(latest.version if latest else 0) + 1, rating=rating, comment=comment, has_owner_reply=has_reply))
                        existing.rating = rating
                        existing.comment = comment
                        existing.review_updated_at = _parse_time(item.get("updateTime"))
                        existing.has_owner_reply = has_reply
                        if has_reply:
                            existing.status = "already_responded"
                db.commit()
                token = data.get("nextPageToken")
                if not token:
                    break
        db.add(AuditLog(action="google_reviews_synced", actor=actor, target_type="system", target_id="google", detail=f"locations={len(locations)};pages={pages};new={imported}"))
        db.commit()
        return {"status": "ok", "locations": len(locations), "pages": pages, "new_reviews": imported}
    finally:
        db.close()
