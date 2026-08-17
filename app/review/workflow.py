from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AIDraft, Approval, AuditLog, Review


@dataclass(frozen=True)
class WorkflowResult:
    review: Review
    draft: AIDraft | None


ALLOWED_ACTIONS = {
    "approve",
    "deny",
    "edit",
    "regenerate",
    "publish",
    "escalate",
    "hold",
    "resume",
}


def _audit(db: Session, action: str, review_id: int, actor: str, detail: str = "") -> None:
    db.add(
        AuditLog(
            action=action,
            actor=actor,
            target_type="review",
            target_id=str(review_id),
            detail=detail,
        )
    )


def latest_draft(db: Session, review_id: int) -> AIDraft | None:
    return db.scalar(
        select(AIDraft)
        .where(AIDraft.review_id == review_id)
        .order_by(AIDraft.created_at.desc(), AIDraft.id.desc())
    )


def apply_action(
    db: Session,
    review_id: int,
    action: str,
    actor: str,
    edited_text: str | None = None,
    comment: str = "",
) -> WorkflowResult:
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Unsupported workflow action: {action}")

    review = db.get(Review, review_id)
    if not review:
        raise ValueError("Review not found")

    draft = latest_draft(db, review_id)

    if action == "edit":
        if not edited_text or not edited_text.strip():
            raise ValueError("Edited response cannot be empty")
        if not draft:
            raise ValueError("Generate a response before editing")
        draft.response_text = edited_text.strip()
        draft.auto_eligible = False
        draft.safety_passed = False
        review.status = "edited"

    elif action == "approve":
        if not draft:
            raise ValueError("No response draft exists")
        review.status = "approved"
        db.add(Approval(review_id=review_id, draft_id=draft.id, action="approve", actor=actor, comment=comment))

    elif action == "deny":
        review.status = "denied"
        db.add(Approval(review_id=review_id, draft_id=draft.id if draft else None, action="deny", actor=actor, comment=comment))

    elif action == "regenerate":
        review.status = "regeneration_requested"
        db.add(Approval(review_id=review_id, draft_id=draft.id if draft else None, action="regenerate", actor=actor, comment=comment))

    elif action == "publish":
        if not draft or not draft.response_text.strip():
            raise ValueError("No valid response is available")
        if not draft.safety_passed:
            raise ValueError("Response must pass the safety gate before publishing")
        review.status = "publish_requested"
        db.add(Approval(review_id=review_id, draft_id=draft.id, action="publish", actor=actor, comment=comment))

    elif action == "escalate":
        review.status = "escalated"
        db.add(Approval(review_id=review_id, draft_id=draft.id if draft else None, action="escalate", actor=actor, comment=comment))

    elif action == "hold":
        review.status = "on_hold"
        db.add(Approval(review_id=review_id, draft_id=draft.id if draft else None, action="hold", actor=actor, comment=comment))

    elif action == "resume":
        review.status = "discovered"
        db.add(Approval(review_id=review_id, draft_id=draft.id if draft else None, action="resume", actor=actor, comment=comment))

    review.updated_at = datetime.now(UTC)
    _audit(db, f"review.{action}", review_id, actor, comment)
    db.commit()
    db.refresh(review)
    return WorkflowResult(review=review, draft=draft)
