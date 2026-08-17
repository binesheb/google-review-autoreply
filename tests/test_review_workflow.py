from app.models import AIDraft, Organization, Location, Review
from app.review.workflow import apply_action


def seed_review(db):
    org = Organization(name="Test Org")
    db.add(org)
    db.flush()
    location = Location(organization_id=org.id, display_name="Main")
    db.add(location)
    db.flush()
    review = Review(
        location_id=location.id,
        source_name="test-review",
        source_review_id="r-1",
        rating=5,
        comment="Great service",
    )
    db.add(review)
    db.flush()
    draft = AIDraft(
        review_id=review.id,
        model="test-model",
        response_text="Thank you for visiting us!",
        safety_passed=True,
        auto_eligible=True,
    )
    db.add(draft)
    db.commit()
    db.refresh(review)
    return review


def test_edit_requires_text(db):
    review = seed_review(db)
    try:
        apply_action(db, review.id, "edit", "tester", edited_text="")
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:
        raise AssertionError("empty edits must be rejected")


def test_edit_invalidates_auto_publish(db):
    review = seed_review(db)
    result = apply_action(db, review.id, "edit", "tester", edited_text="Edited response")
    assert result.review.status == "edited"
    assert result.draft.response_text == "Edited response"
    assert result.draft.safety_passed is False
    assert result.draft.auto_eligible is False


def test_approve_records_decision(db):
    review = seed_review(db)
    result = apply_action(db, review.id, "approve", "manager", comment="Looks good")
    assert result.review.status == "approved"


def test_publish_requires_safety(db):
    review = seed_review(db)
    result = apply_action(db, review.id, "edit", "tester", edited_text="Needs review")
    assert result.review.status == "edited"
    try:
        apply_action(db, review.id, "publish", "tester")
    except ValueError as exc:
        assert "safety gate" in str(exc)
    else:
        raise AssertionError("unsafe draft must not publish")
