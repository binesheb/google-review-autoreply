from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

def now():
    return datetime.now(timezone.utc)

class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    google_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    store_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_publish: Mapped[bool] = mapped_column(Boolean, default=False)
    reviews = relationship("Review", back_populates="location")

class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    google_name: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    google_review_id: Mapped[str] = mapped_column(String(255), index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    reviewer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text, default="")
    review_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    has_google_reply: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(50), default="discovered", index=True)
    risk_level: Mapped[str] = mapped_column(String(20), default="unknown")
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    location = relationship("Location", back_populates="reviews")
    drafts = relationship("AIDraft", back_populates="review", order_by="AIDraft.created_at")

class AIDraft(Base):
    __tablename__ = "ai_drafts"
    id: Mapped[int] = mapped_column(primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), index=True)
    model: Mapped[str] = mapped_column(String(255))
    response_text: Mapped[str] = mapped_column(Text)
    safety_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_reasons: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    review = relationship("Review", back_populates="drafts")

class Approval(Base):
    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), index=True)
    action: Mapped[str] = mapped_column(String(40))
    actor: Mapped[str] = mapped_column(String(255), default="system")
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    scope: Mapped[str] = mapped_column(String(255), default="company")
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    source: Mapped[str] = mapped_column(String(500), default="manual")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class Case(Base):
    __tablename__ = "cases"
    id: Mapped[int] = mapped_column(primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), index=True)
    category: Mapped[str] = mapped_column(String(100))
    priority: Mapped[str] = mapped_column(String(30), default="medium")
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="open")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(100))
    actor: Mapped[str] = mapped_column(String(255), default="system")
    target_type: Mapped[str] = mapped_column(String(100))
    target_id: Mapped[str] = mapped_column(String(255))
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class SystemSetting(Base):
    __tablename__ = "system_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text)
    updated_by: Mapped[str] = mapped_column(String(255), default="system")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
