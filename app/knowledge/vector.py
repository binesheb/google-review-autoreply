from __future__ import annotations

from hashlib import sha256

import httpx

from app.core.config import settings


class EmbeddingClient:
    def __init__(self) -> None:
        self.base_url = settings.ai_base_url.rstrip("/")
        self.model = settings.embedding_model

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = httpx.post(
            f"{self.base_url}/api/embed",
            json={"model": self.model, "input": texts},
            timeout=180,
        )
        response.raise_for_status()
        return response.json()["embeddings"]


class QdrantStore:
    def __init__(self) -> None:
        self.base_url = settings.qdrant_url.rstrip("/")
        self.collection = settings.qdrant_collection

    def _collection_url(self) -> str:
        return f"{self.base_url}/collections/{self.collection}"

    def ensure_collection(self, vector_size: int) -> None:
        response = httpx.get(self._collection_url(), timeout=15)
        if response.status_code == 200:
            return
        if response.status_code != 404:
            response.raise_for_status()
        response = httpx.put(
            self._collection_url(),
            json={"vectors": {"size": vector_size, "distance": "Cosine"}},
            timeout=30,
        )
        response.raise_for_status()

    def upsert(self, points: list[dict]) -> None:
        if not points:
            return
        self.ensure_collection(len(points[0]["vector"]))
        response = httpx.put(
            f"{self._collection_url()}/points?wait=true",
            json={"points": points},
            timeout=60,
        )
        response.raise_for_status()

    def search(self, vector: list[float], organization_id: int, limit: int) -> list[dict]:
        response = httpx.post(
            f"{self._collection_url()}/points/query",
            json={
                "query": vector,
                "limit": limit,
                "with_payload": True,
                "filter": {
                    "must": [
                        {"key": "organization_id", "match": {"value": organization_id}},
                    ]
                },
            },
            timeout=30,
        )
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return response.json().get("result", {}).get("points", [])


def chunk_text(text: str, size: int = 1200, overlap: int = 200) -> list[str]:
    clean = " ".join(text.split())
    if not clean:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + size)
        chunks.append(clean[start:end])
        if end == len(clean):
            break
        start = max(0, end - overlap)
    return chunks


def point_id(knowledge_id: int, chunk_index: int) -> int:
    digest = sha256(f"knowledge:{knowledge_id}:{chunk_index}".encode()).hexdigest()
    return int(digest[:15], 16)
