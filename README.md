# Jayalakshmi Review Intelligence & Response Platform

A self-hosted Google Business Profile review intelligence and response platform for Jayalakshmi Silks.

## What this replaces

The original repository was a small Flask/OpenAI prototype that accepted one review and returned one generated reply. This branch replaces that prototype with the architecture agreed in the project SRS: multi-location review ingestion, historical backlog support, verified knowledge/RAG, local-model abstraction, deterministic safety gates, approvals, complaint cases, auditability, analytics foundations, and a responsive control dashboard.

## Design principles

- **Local-first AI:** the application does not require a hosted LLM. The AI provider is an interface; the first production target is a local HTTP-compatible model runtime on the Windows AI PC.
- **Knowledge is separate from model training:** changing store facts does not require retraining.
- **AI drafts; rules govern publishing:** deterministic policy checks sit outside the model.
- **Fail closed:** if critical safety, database, or knowledge services are unavailable, automatic publishing is not allowed.
- **Human control:** approval, edit, reject, regenerate, escalate and global pause are first-class operations.
- **Learning is controlled:** human corrections become training candidates, but the live model never retrains itself automatically.

## Current repository layout

```text
app/
  api/                 HTTP endpoints
  ai/                  model provider, prompt and safety logic
  core/                configuration and security helpers
  knowledge/           knowledge retrieval interface
  google/              Google Business Profile client
  db/                  SQLAlchemy models/session
  main.py              FastAPI application
config/
  REVIEW_INSTRUCTIONS.md
  automation.yaml
knowledge/
  README.md
frontend/
  index.html
Dockerfile
docker-compose.yml
pyproject.toml
.env.example
tests/
.github/workflows/ci.yml
```

## Learning mode

This repository is intentionally structured so each layer can be studied independently. Before adding production integrations, understand the data flow:

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

## Development

1. Copy `.env.example` to `.env`.
2. Start PostgreSQL and Qdrant with `docker compose up -d postgres qdrant`.
3. Install Python dependencies with `pip install -e .`.
4. Start the API with `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.
5. Open `http://localhost:8000` for the control dashboard and `http://localhost:8000/docs` for the API documentation.

Google credentials are deliberately not committed. The Google connector remains disabled until OAuth credentials and verified Business Profile locations are configured.

## Important production gate

The application starts in **draft-only / shadow-safe mode**. Do not enable public auto-publishing until the historical dry run, golden benchmark, Google reconciliation tests and approval workflow have been validated.

## Official Google references

- Business Profile APIs: https://developers.google.com/my-business
- Reviews resource: https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews
- Review list: https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/list
- Reply update: https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/updateReply
