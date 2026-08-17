# Review response workflow

The review workflow is deliberately stateful and auditable.

## Supported operator actions

- **Approve** — approve the current draft for the next publishing step.
- **Deny** — reject the current draft and retain the decision in the audit trail.
- **Edit** — manually modify the response; edited drafts are not considered safe for automatic publishing until revalidated.
- **Regenerate** — request a new response while preserving the previous draft and reason for regeneration.
- **Escalate** — route a review to a human owner/case workflow.
- **Hold** — pause processing without losing the review.
- **Resume** — return a held review to the active queue.
- **Publish** — request publication only after the response has passed the deterministic safety gate.

Every operator decision is recorded as an approval event and an audit event. Drafts are immutable history records; a regenerated response should create a new `AIDraft` rather than overwrite the previous one.

The workflow intentionally separates AI generation from publication authority: an AI model may propose text, but deterministic policy and human approval govern whether that text can be published.
