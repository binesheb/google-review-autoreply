from sqlalchemy import select
from sqlalchemy.orm import Session
from app.ai.provider import LocalAI, load_instructions
from app.ai.rules import classify, validate_response
from app.core.config import settings
from app.knowledge.service import KnowledgeService
from app.models import AIDraft, AuditLog, InstructionSet, Organization, Review


class ResponseService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = LocalAI()
        self.knowledge = KnowledgeService(db)

    def _instructions(self) -> tuple[str, str]:
        org = self.db.scalar(select(Organization).order_by(Organization.id.asc()))
        if org:
            item = self.db.scalar(
                select(InstructionSet)
                .where(InstructionSet.organization_id == org.id, InstructionSet.status == "active")
                .order_by(InstructionSet.created_at.desc())
            )
            if item:
                return item.content, item.version
        return load_instructions(), "file-default"

    def draft(self, review: Review) -> AIDraft:
        risk, _ = classify(review.comment, review.rating)
        facts = self.knowledge.retrieve(review.comment, scope=review.location.display_name)
        evidence = "\n".join(f"- {x.title}: {x.content}" for x in facts) or "No verified fact found. Do not invent facts."
        instructions, instruction_version = self._instructions()
        prompt = f"""You are the review response assistant for {settings.app_name}.

MASTER INSTRUCTIONS:
{instructions}

REVIEW:
Rating: {review.rating}/5
Customer: {review.reviewer_name or 'Customer'}
Location: {review.location.display_name}
Text: {review.comment or '[No text]'}

VERIFIED KNOWLEDGE:
{evidence}

RISK CLASSIFICATION: {risk}

Write only the proposed public owner reply. Never invent facts, refunds, compensation, contact details or actions that are not supported by the instructions or verified knowledge.
"""
        response = self.ai.generate(prompt)
        safety = validate_response(response, review.rating, review.comment, settings.auto_publish_enabled and review.location.auto_publish)
        draft = AIDraft(
            review_id=review.id,
            model=self.ai.model,
            instruction_version=instruction_version,
            response_text=response,
            evidence=evidence,
            safety_passed=safety.passed,
            auto_eligible=safety.auto_eligible,
            risk_reasons=";".join(safety.reasons),
        )
        self.db.add(draft)
        self.db.add(AuditLog(action="ai_draft_created", target_type="review", target_id=str(review.id), detail=f"model={self.ai.model};instructions={instruction_version};risk={risk};eligible={safety.auto_eligible}"))
        self.db.commit()
        self.db.refresh(draft)
        return draft
