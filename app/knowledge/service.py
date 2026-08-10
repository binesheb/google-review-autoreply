from datetime import UTC, datetime

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.knowledge.vector import EmbeddingClient, QdrantStore, chunk_text, point_id
from app.models import KnowledgeItem, Organization


class KnowledgeService:
    """Semantic retrieval with a lexical fallback when vector services are unavailable."""

    def __init__(self, db: Session):
        self.db = db
        self.embeddings = EmbeddingClient()
        self.vectors = QdrantStore()

    def index(self, item: KnowledgeItem) -> None:
        chunks = chunk_text(item.content)
        if not chunks:
            return
        self.vectors.delete_knowledge(item.id)
        vectors = self.embeddings.embed(chunks)
        points = [
            {
                "id": point_id(item.id, index),
                "vector": vector,
                "payload": {
                    "knowledge_id": item.id,
                    "organization_id": item.organization_id,
                    "scope": item.scope,
                    "title": item.title,
                    "content": chunk,
                },
            }
            for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True))
        ]
        self.vectors.upsert(points)

    def retrieve(self, query: str, scope: str | None = None, limit: int = 5) -> list[KnowledgeItem]:
        org = self.db.scalar(select(Organization).order_by(Organization.id.asc()))
        if not org:
            return []
        now = datetime.now(UTC)

        try:
            query_vector = self.embeddings.embed([query])[0]
            hits = self.vectors.search(query_vector, org.id, max(limit * 3, 10))
            ids: list[int] = []
            for hit in hits:
                payload = hit.get("payload") or {}
                item_id = payload.get("knowledge_id")
                item_scope = payload.get("scope", "organization")
                if not isinstance(item_id, int):
                    continue
                if scope and item_scope not in ("organization", "company", scope):
                    continue
                if item_id not in ids:
                    ids.append(item_id)
                if len(ids) >= limit:
                    break
            if ids:
                items = self.db.scalars(
                    select(KnowledgeItem).where(KnowledgeItem.id.in_(ids))
                ).all()
                by_id = {item.id: item for item in items}
                return [
                    item
                    for item_id in ids
                    if (item := by_id.get(item_id))
                    and item.status == "active"
                    and (not item.expires_at or item.expires_at > now)
                ]
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            pass

        return self._lexical_retrieve(query, org.id, scope, limit, now)

    def _lexical_retrieve(
        self,
        query: str,
        organization_id: int,
        scope: str | None,
        limit: int,
        now: datetime,
    ) -> list[KnowledgeItem]:
        items = list(
            self.db.scalars(
                select(KnowledgeItem).where(
                    KnowledgeItem.organization_id == organization_id,
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
        scored.sort(key=lambda value: value[0], reverse=True)
        return [item for score, item in scored[:limit] if score > 0]
