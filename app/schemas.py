from datetime import datetime
from pydantic import BaseModel, Field

class ReviewIn(BaseModel):
    google_name: str
    google_review_id: str
    location_name: str
    reviewer_name: str | None = None
    rating: int = Field(ge=1, le=5)
    comment: str = ""
    review_created_at: datetime | None = None
    review_updated_at: datetime | None = None
    has_google_reply: bool = False

class DraftRequest(BaseModel):
    review_id: int

class DraftResponse(BaseModel):
    review_id: int
    draft_id: int
    response: str
    safety_passed: bool
    auto_eligible: bool
    reasons: list[str]

class ActionRequest(BaseModel):
    actor: str = "dashboard"
    comment: str = ""
