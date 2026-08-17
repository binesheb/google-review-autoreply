from pydantic import BaseModel, Field


class ReviewActionRequest(BaseModel):
    actor: str = Field(default="dashboard")
    comment: str = Field(default="", max_length=2000)
    edited_text: str | None = Field(default=None, max_length=10000)


class RegenerateRequest(BaseModel):
    actor: str = Field(default="dashboard")
    reason: str = Field(min_length=3, max_length=2000)
    tone: str | None = Field(default=None, max_length=100)
    focus: str | None = Field(default=None, max_length=1000)
    constraints: str | None = Field(default=None, max_length=2000)
