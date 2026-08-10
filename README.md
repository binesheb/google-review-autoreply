# Jayalakshmi Review Intelligence & Response Platform

A self-hosted Google Business Profile review intelligence and response platform for Jayalakshmi Silks.

## What this replaces

The original repository was a small Flask/OpenAI prototype that accepted one review and returned one generated reply. The platform is now structured for multi-location review ingestion, historical backlog support, verified knowledge/RAG, local-model abstraction, deterministic safety gates, approvals, complaint cases, auditability, analytics foundations and future multi-location operation.

## One-command Linux deployment

The target deployment is a clean Linux server with Docker. The installer installs Docker Engine + Compose when needed, pulls the application from GitHub, creates persistent configuration, builds the containers and starts the server.

```bash
curl -fsSL https://raw.githubusercontent.com/binesheb/google-review-autoreply/main/install.sh | sudo bash
```

Deployment details are documented in `DEPLOYMENT.md`.

## Architecture

```text
Google Business Profile
        ↓
Review ingestion
        ↓
PostgreSQL review ledger
        ↓
Classification + policy
        ↓
Verified knowledge retrieval
        ↓
Local AI draft
        ↓
Deterministic safety gate
        ↓
Approval OR auto-publish
        ↓
Google owner reply
        ↓
Audit + learning candidate + analytics
```

## Design principles

- **Local-first AI:** the application does not require a hosted LLM. The AI provider is an interface; the first production target is a local HTTP-compatible model runtime.
- **Knowledge is separate from model training:** changing store facts does not require retraining.
- **AI drafts; rules govern publishing:** deterministic policy checks sit outside the model.
- **Fail closed:** if critical safety, database or knowledge services are unavailable, automatic publishing is not allowed.
- **Human control:** approval, edit, reject, regenerate, escalate and global pause are first-class operations.
- **Learning is controlled:** human corrections become training candidates, but the live model never retrains itself automatically.
- **Installer-first operations:** deployment should be reproducible from GitHub rather than depend on manual server setup.

## Services

```text
Docker Compose
├── API + Dashboard
├── PostgreSQL
└── Qdrant
```

## Development

1. Copy `.env.example` to `.env`.
2. Start PostgreSQL and Qdrant with `docker compose up -d postgres qdrant`.
3. Install Python dependencies with `pip install -e .`.
4. Start the API with `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.
5. Open `http://localhost:8000` for the control dashboard and `http://localhost:8000/docs` for the API documentation.

## Important production gate

The application starts in **draft-only / shadow-safe mode**. Do not enable public auto-publishing until the historical dry run, golden benchmark, Google reconciliation tests, authentication and approval workflow have been validated.

Google credentials are deliberately not committed. The Google connector remains disabled until OAuth credentials and verified Business Profile locations are configured.

## Official Google references

- Business Profile APIs: https://developers.google.com/my-business
- Reviews resource: https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews
- Review list: https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/list
- Reply update: https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/updateReply
