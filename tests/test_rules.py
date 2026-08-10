from app.ai.rules import classify, validate_response


def test_low_rating_requires_approval():
    risk, reasons = classify("Very poor service", 1)
    assert risk == "high"
    result = validate_response("Thank you for sharing your feedback.", 1, "Very poor service", True)
    assert result.passed
    assert not result.auto_eligible
    assert "negative_review_requires_approval" in result.reasons


def test_high_risk_keyword_blocks_auto_publish():
    result = validate_response(
        "Thank you for your feedback.", 5, "We will contact our lawyer and go to court.", True
    )
    assert result.passed
    assert not result.auto_eligible
    assert "high_risk_review_requires_escalation" in result.reasons


def test_prohibited_promise_fails():
    result = validate_response("We will refund you immediately.", 5, "Great service", True)
    assert not result.passed
