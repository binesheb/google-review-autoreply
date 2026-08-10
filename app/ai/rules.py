import re
from dataclasses import dataclass

HIGH_RISK = [
    "lawyer",
    "legal",
    "court",
    "police",
    "consumer forum",
    "consumer court",
    "injury",
    "accident",
    "discrimination",
    "harassment",
    "fraud",
    "scam",
    "stolen",
    "threat",
    "compensation",
    "refund",
    "chargeback",
    "media",
    "press",
]
PROHIBITED_PATTERNS = [
    r"\bwe will refund\b",
    r"\bwe guarantee\b",
    r"\blegal liability\b",
    r"\bcontact me at\b",
    r"\bcall me at\b",
]


@dataclass
class SafetyResult:
    passed: bool
    auto_eligible: bool
    reasons: list[str]
    risk_level: str


def classify(review_text: str, rating: int) -> tuple[str, list[str]]:
    text = review_text.lower()
    reasons = [f"rating:{rating}"]
    if rating <= 2:
        reasons.append("low_rating")
    if any(term in text for term in HIGH_RISK):
        reasons.append("high_risk_keyword")
    if rating == 3:
        reasons.append("mixed_rating")
    if rating >= 4 and not any(term in text for term in HIGH_RISK):
        return "low", reasons
    return ("high" if rating <= 2 or "high_risk_keyword" in reasons else "medium"), reasons


def validate_response(
    response: str, rating: int, review_text: str, auto_enabled: bool
) -> SafetyResult:
    reasons: list[str] = []
    lower = response.lower()
    for pattern in PROHIBITED_PATTERNS:
        if re.search(pattern, lower):
            reasons.append(f"prohibited_pattern:{pattern}")
    if len(response.split()) > 100:
        reasons.append("response_too_long")
    if rating <= 2:
        reasons.append("negative_review_requires_approval")
    if rating == 3:
        reasons.append("mixed_review_requires_approval")
    if any(term in review_text.lower() for term in HIGH_RISK):
        reasons.append("high_risk_review_requires_escalation")
    passed = not any(
        x.startswith("prohibited_pattern") or x == "response_too_long" for x in reasons
    )
    auto_eligible = (
        passed and auto_enabled and rating >= 4 and not any("requires_" in x for x in reasons)
    )
    return SafetyResult(passed, auto_eligible, reasons, "high" if reasons else "low")
