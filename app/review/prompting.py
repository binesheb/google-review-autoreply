from __future__ import annotations

from dataclasses import dataclass

from app.models import AIDraft, InstructionSet, Review


@dataclass(frozen=True)
class RegenerationRequest:
    reason: str
    tone: str | None = None
    focus: str | None = None
    constraints: str | None = None


def build_regeneration_instruction(
    review: Review,
    draft: AIDraft | None,
    request: RegenerationRequest,
    instructions: InstructionSet | None = None,
) -> str:
    parts = [
        "Regenerate the proposed business review response.",
        f"Review rating: {review.rating}/5.",
        f"Review text: {review.comment}",
        f"Reason for regeneration: {request.reason}",
    ]
    if draft:
        parts.append(f"Previous response to improve: {draft.response_text}")
    if request.tone:
        parts.append(f"Preferred tone: {request.tone}")
    if request.focus:
        parts.append(f"Focus on: {request.focus}")
    if request.constraints:
        parts.append(f"Additional constraints: {request.constraints}")
    if instructions:
        parts.append(f"Active business instructions: {instructions.content}")
    return "\n\n".join(parts)
