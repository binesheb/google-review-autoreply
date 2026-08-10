# Review Intelligence Platform

A self-hosted, local-first platform for Google Business Profile review monitoring, AI-assisted response, approval workflows, complaint routing, knowledge management and reputation intelligence.

The repository is intentionally **company-neutral**. A company, hotel group, retailer, clinic, restaurant chain or other organisation can install the same product and configure its own organisation, locations, policies, AI instructions and integrations.

## One-command Linux installation

On a clean Ubuntu/Debian server:

```bash
curl -fsSL https://raw.githubusercontent.com/binesheb/google-review-autoreply/main/install.sh | sudo bash
```

The installer is interactive on first install and asks for configurable deployment values such as:

- Product / organisation name
- Admin username
- Admin password
- Web port
- Timezone
- Installation directory
- Local AI model
- Initial auto-publishing policy

A non-interactive mode is also supported through environment variables for automated deployments.

## Product architecture

```text
Review Source(s)
      ↓
Ingestion + Reconciliation
      ↓
Review Ledger (PostgreSQL)
      ↓
Language / Topic / Risk Classification
      ↓
Verified Knowledge Retrieval
      ↓
Local Embeddings + Qdrant
      ↓
Local AI Response Draft
      ↓
Deterministic Safety Gate
      ↓
Auto Publish / Approval / Escalation
      ↓
Owner Reply + Internal Case
      ↓
Audit + Learning Dataset + Analytics
```

## Product principles

1. **Generic core** — no company name, store names, passwords or Google credentials are hard-coded.
2. **Installer-first** — a fresh Linux server should be deployable without manually installing Python, PostgreSQL, Qdrant or the AI runtime.
3. **Configuration separation** — infrastructure settings belong to installation configuration; business behaviour belongs in the dashboard and database.
4. **Local-first AI** — the first deployment target is a local model runtime. The AI provider is replaceable.
5. **Knowledge is not model training** — changing business facts should not require retraining.
6. **AI drafts; rules govern publishing** — deterministic checks remain outside the model.
7. **Fail closed** — critical safety or infrastructure failures disable automatic publication.
8. **Human control** — approval, editing, rejection, escalation and global pause are first-class operations.
9. **Controlled learning** — human corrections become training candidates; the live model never retrains itself silently.
10. **Upgrade-safe** — database schema changes are managed through Alembic migrations; persistent PostgreSQL, Qdrant and Ollama volumes survive application upgrades.

## Deployment services

```text
Docker Compose
├── API + Dashboard
├── PostgreSQL
├── Qdrant
└── Ollama
    ├── Response model
    └── Embedding model
```

The default deployment exposes only the application port. PostgreSQL, Qdrant and Ollama remain on the internal Docker network.

## Configuration model

### Installation-time configuration

Examples:

```text
APP_NAME
ADMIN_USERNAME
ADMIN_PASSWORD_HASH
SECRET_KEY
APP_PORT
APP_TIMEZONE
INSTALL_DIR
AI_MODEL
EMBEDDING_MODEL
AUTO_PUBLISH_ENABLED
```

### Runtime business configuration

Managed from the dashboard:

```text
Organisation
Locations
Review sources
AI instructions
Knowledge base
Safety rules
Approval rules
Automation
Notifications
Integrations
```

Secrets are never committed to GitHub. Authentication uses a signed, expiring, HTTP-only session cookie.

## Development

```bash
cp .env.example .env
docker compose up -d
pip install -e '.[test]'
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Dashboard: `http://localhost:8000/`

API documentation: `http://localhost:8000/docs`

Database migrations:

```bash
alembic upgrade head
```

## Production rollout

The default policy is safe: **draft / approval mode** and Google publishing disabled.

Recommended rollout:

```text
Install
  ↓
Configure organisation
  ↓
Connect Google
  ↓
Import historical reviews
  ↓
Dry run
  ↓
Shadow mode
  ↓
Human approval
  ↓
Limited auto-publish
  ↓
Expanded automation
```

## Current production-readiness boundary

The core standalone deployment is now covered by automated tests, Ruff quality gates, Python module compilation, Docker Compose validation and a production Docker build in GitHub Actions.

Before an internet-facing production rollout, the remaining operational controls to complete are:

- Google OAuth/token lifecycle rather than manual access-token configuration
- TLS/reverse proxy and domain configuration
- stronger multi-user RBAC and 2FA
- encrypted integration credentials
- automated PostgreSQL/Qdrant backup and restore testing
- monitoring/alerting and scheduled automation workers
- broader review-source connectors

## Official Google references

- https://developers.google.com/my-business
- https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews
- https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/list
- https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/updateReply
