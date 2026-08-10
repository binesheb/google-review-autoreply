from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import KnowledgeItem, Organization


class KnowledgeService:
    """V1 deterministic retrieval. A vector/embedding retriever can replace this interface later."""

    def __init__(self, db: Session):
        self.db = db

    def retrieve(self, query: str, scope: str | None = None, limit: int = 5) -> list[KnowledgeItem]:
        org = self.db.scalar(select(Organization).order_by(Organization.id.asc()))
        if not org:
            return []
        now = datetime.now(UTC)
        items = list(
            self.db.scalars(
                select(KnowledgeItem).where(
                    KnowledgeItem.organization_id == org.id,
                    KnowledgeItem.status == "active",
                )
            ).all()
        )
        q = set(query.lower().split())
        scored = []
        for item in items:
            if item.expires_at and item.expires_at <= now:
                continue
            if scope and item.scope not in ("organization", "company", scope):
                continue
            score = len(q.intersection(set(item.content.lower().split())))
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored[:limit] if score > 0]
