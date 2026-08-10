import httpx

BASE = "https://mybusiness.googleapis.com/v4"


class GoogleBusinessProfileClient:
    """Thin REST client. OAuth/token persistence is intentionally kept outside this class."""

    def __init__(self, access_token: str):
        self.access_token = access_token

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.access_token}", "Accept": "application/json"}

    def list_reviews(self, location_name: str, page_token: str | None = None, page_size: int = 50):
        params = {"pageSize": min(page_size, 50), "orderBy": "updateTime desc"}
        if page_token:
            params["pageToken"] = page_token
        r = httpx.get(
            f"{BASE}/{location_name}/reviews", headers=self.headers, params=params, timeout=30
        )
        r.raise_for_status()
        return r.json()

    def update_reply(self, review_name: str, comment: str):
        r = httpx.put(
            f"{BASE}/{review_name}/reply",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"comment": comment},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def get_review(self, review_name: str):
        r = httpx.get(f"{BASE}/{review_name}", headers=self.headers, timeout=30)
        r.raise_for_status()
        return r.json()
