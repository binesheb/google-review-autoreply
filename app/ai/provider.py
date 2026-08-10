from pathlib import Path
import httpx
from app.core.config import settings, ROOT

class LocalAI:
    """Small provider adapter for an Ollama-compatible local HTTP API.

    The rest of the application only knows this interface. That lets us swap
    llama.cpp, Ollama or another local server without rewriting business logic.
    """
    def __init__(self):
        self.base_url = settings.ai_base_url.rstrip("/")
        self.model = settings.ai_model

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {"model": self.model, "stream": False,
                   "messages": [{"role": "user", "content": prompt}]}
        headers = {"Authorization": f"Bearer {settings.ai_api_key}"} if settings.ai_api_key else {}
        r = httpx.post(url, json=payload, headers=headers, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data["message"]["content"].strip()


def load_instructions() -> str:
    path = ROOT / "config" / "REVIEW_INSTRUCTIONS.md"
    return path.read_text(encoding="utf-8")
