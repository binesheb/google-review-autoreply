from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import ROOT
from app.models import KnowledgeItem

class KnowledgeService:
    """V1 keyword retrieval. Qdrant embeddings can replace this without changing callers."""
    def __init__(self, db: Session):
        self.db = db

    def retrieve(self, query: str, scope: str | None = None, limit: int = 5) -> list[KnowledgeItem]:
        items = list(self.db.scalars(select(KnowledgeItem).where(KnowledgeItem.status == "active")).all())
        q = set(query.lower().split())
        scored = []
        for item in items:
            if scope and item.scope not in ("company", scope):
                continue
            score = len(q.intersection(set(item.content.lower().split())))
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored[:limit] if score > 0]

    def load_seed_markdown(self) -> str:
        path = ROOT / "knowledge" / "README.md"
        return path.read_text(encoding="utf-8")
