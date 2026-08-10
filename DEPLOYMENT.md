# Linux Deployment

The platform is designed to be provisioned as a Docker Compose stack. The target experience is a clean Linux server where one bootstrap command installs the runtime, pulls the current repository, creates persistent configuration, downloads the local AI model and starts the server.

## One-command installation

```bash
curl -fsSL https://raw.githubusercontent.com/binesheb/google-review-autoreply/main/install.sh | sudo bash
```

The installer currently targets Debian/Ubuntu hosts. Docker Engine and the Docker Compose plugin are installed from Docker's official APT repository when they are missing. The application is then downloaded from the `main` branch and deployed under `/opt/jayalakshmi-review`.

## What gets deployed

```text
Linux server
   │
   └── Docker Engine
        ├── API + Dashboard
        ├── PostgreSQL       ← persistent review/audit data
        ├── Qdrant           ← knowledge/vector storage foundation
        └── Ollama           ← local AI runtime
             └── qwen3:4b    ← initial local model
```

The official Ollama Docker image supports CPU-only deployment and GPU-specific configurations. The initial stack deliberately uses CPU-compatible Ollama so the same installer works on ordinary Linux servers; GPU acceleration can be added later without changing the application/provider interface. citeturn3search2turn3search0

The model is downloaded by the one-shot `ollama-init` container during deployment. The model files are stored in the persistent `ollama_data` volume.

## Data persistence

PostgreSQL, Qdrant and Ollama use Docker named volumes. Rerunning the installer does not intentionally delete these volumes.

Persistence is not a backup. A later production milestone will add a versioned backup/restore command and scheduled off-server backups.

## Configuration

The installer creates `.env` from `.env.example` on the first installation and generates a random `SECRET_KEY`. Subsequent installations preserve the existing `.env`.

The container network uses service names rather than `localhost`:

- PostgreSQL: `postgres:5432`
- Qdrant: `qdrant:6333`
- Ollama: `ollama:11434`

Production Google credentials are never committed to GitHub. Google integration and public auto-publishing remain disabled by default.

## Updating

The installer is idempotent. Rerunning the same command downloads the current `main` branch and rebuilds the application while preserving `.env` and Docker volumes.

For normal operations:

```bash
jayalakshmi-review ps
jayalakshmi-review logs -f api
jayalakshmi-review logs -f ollama
jayalakshmi-review up -d --build
```

## GPU path

The default stack is CPU-compatible. For NVIDIA systems, the next deployment milestone will add an optional Compose override that enables the NVIDIA Container Toolkit and `--gpus=all`; Ollama documents this container configuration officially. citeturn3search2

## Production hardening before public exposure

The current installer is intended for controlled deployment/testing. Before exposing the dashboard to the public internet, we will add:

- HTTPS with a reverse proxy
- administrator authentication and role-based access
- secure secret handling
- firewall policy
- automated database backups
- update/rollback support
- monitoring and alerting
- Google OAuth token encryption
- signed release/version pinning

Docker documents supported Linux Engine installation paths for Ubuntu and Debian and warns that published container ports can bypass some host firewall rules. We therefore should not treat a raw `:8000` deployment as the final internet-facing production configuration. citeturn0search0turn1search0
