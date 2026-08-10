from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.config import settings
from app.db import SessionLocal
from app.models import Location, Review
from app.google.client import GoogleBusinessProfileClient

router = APIRouter(prefix="/api/google", tags=["google"])
RATING_MAP = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}

def _parse_time(value):
    if not value: return None
    try: return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError: return None

@router.post("/sync")
def sync_reviews():
    if not settings.google_enabled or not settings.google_access_token:
        raise HTTPException(503, "Google integration is not configured")
    db = SessionLocal(); imported = 0; pages = 0
    try:
        client = GoogleBusinessProfileClient(settings.google_access_token)
        locations = db.scalars(select(Location).where(Location.enabled == True)).all()  # noqa: E712
        for location in locations:
            token = None
            while True:
                data = client.list_reviews(location.google_name, token, 50)
                pages += 1
                for item in data.get("reviews", []):
                    reviewer = item.get("reviewer") or {}
                    reply = item.get("reviewReply")
                    existing = db.scalar(select(Review).where(Review.google_name == item.get("name")))
                    if not existing:
                        existing = Review(
                            google_name=item.get("name"), google_review_id=item.get("reviewId", ""),
                            location_id=location.id, reviewer_name=reviewer.get("displayName"),
                            rating=RATING_MAP.get(item.get("starRating"), 0), comment=item.get("comment", ""),
                            review_created_at=_parse_time(item.get("createTime")), review_updated_at=_parse_time(item.get("updateTime")),
                            has_google_reply=bool(reply), status="already_responded" if reply else "queued")
                        db.add(existing); imported += 1
                    else:
                        existing.rating = RATING_MAP.get(item.get("starRating"), existing.rating)
                        existing.comment = item.get("comment", "")
                        existing.has_google_reply = bool(reply)
                        if reply: existing.status = "already_responded"
                db.commit()
                token = data.get("nextPageToken")
                if not token: break
        return {"status": "ok", "locations": len(locations), "pages": pages, "new_reviews": imported}
    finally:
        db.close()
