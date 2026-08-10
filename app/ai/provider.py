import httpx

from app.core.config import ROOT, settings


class LocalAI:
    """Provider adapter for an Ollama-compatible local HTTP API.

    Business logic depends only on this small interface so the runtime can be
    replaced later without rewriting review workflows.
    """

    def __init__(self):
        self.base_url = settings.ai_base_url.rstrip("/")
        self.model = settings.ai_model

    def generate(self, prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "stream": False,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"].strip()


def load_instructions() -> str:
    path = ROOT / "config" / "REVIEW_INSTRUCTIONS.md"
    return path.read_text(encoding="utf-8")
