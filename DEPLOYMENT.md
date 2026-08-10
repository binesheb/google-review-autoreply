# Linux Deployment

The platform is designed to be provisioned as a Docker Compose stack. The target experience is a clean Linux server where one bootstrap command installs the runtime, pulls the current repository, creates persistent configuration, builds the application and starts the services.

## One-command installation

```bash
curl -fsSL https://raw.githubusercontent.com/binesheb/google-review-autoreply/main/install.sh | sudo bash
```

The installer currently targets Debian/Ubuntu hosts. Docker Engine and the Docker Compose plugin are installed from Docker's official APT repository when they are missing. The application itself is then downloaded from the `main` branch and deployed under `/opt/jayalakshmi-review`.

## What gets deployed

```text
Linux server
   │
   └── Docker Engine
        ├── API / Dashboard
        ├── PostgreSQL      ← persistent review/audit data
        └── Qdrant          ← knowledge/vector storage foundation
```

The database and vector-store data live in Docker named volumes, so rerunning the installer does not intentionally remove application data.

## Configuration

The installer creates `.env` from `.env.example` on the first installation and generates a random `SECRET_KEY`. Subsequent installations preserve the existing `.env`.

Production Google credentials are never committed to GitHub. Google integration and public auto-publishing remain disabled by default.

## Updating

The installer is idempotent. Rerunning the same command downloads the current `main` branch and rebuilds the application while preserving `.env` and Docker volumes.

For normal operations:

```bash
jayalakshmi-review ps
jayalakshmi-review logs -f api
jayalakshmi-review pull
jayalakshmi-review up -d --build
```

## Backup principle

PostgreSQL and Qdrant data are persistent, but persistence is not a backup. A later production milestone will add a versioned backup/restore command and scheduled off-server backups.

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

Docker documents supported Linux Engine installation paths for Ubuntu and Debian and warns that published container ports can bypass some host firewall rules. We therefore should not treat a raw `:8000` deployment as the final internet-facing production configuration.
