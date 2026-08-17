from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Review


QUEUE_STATUSES = (
    "discovered",
    "drafted",
    "edited",
    "approved",
    "denied",
    "regeneration_requested",
    "escalated",
    "on_hold",
    "publish_requested",
)


def list_queue(db: Session, status: str | None = None, limit: int = 50) -> list[Review]:
    stmt = select(Review).order_by(Review.updated_at.desc()).limit(max(1, min(limit, 200)))
    if status:
        if status not in QUEUE_STATUSES:
            raise ValueError(f"Unsupported queue status: {status}")
        stmt = stmt.where(Review.status == status)
    else:
        stmt = stmt.where(Review.status.in_(QUEUE_STATUSES))
    return list(db.scalars(stmt).all())
