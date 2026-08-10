# Deployment

## Supported first-class target

- Ubuntu
- Debian
- Docker Engine + Docker Compose plugin

The installer is designed to bootstrap a clean server with one command.

```bash
curl -fsSL https://raw.githubusercontent.com/binesheb/google-review-autoreply/main/install.sh | sudo bash
```

## First install

The installer asks for:

- Product / organisation-facing name
- Administrator username
- Administrator password
- Web port
- Timezone
- Local AI model
- Initial automatic-publishing preference
- Installation directory

It generates a random application secret and database password. The `.env` file is created with mode `600`.

## Non-interactive deployment

For automated infrastructure, values can be supplied as environment variables:

```bash
APP_NAME="Review Intelligence Platform" \
APP_PORT=8080 \
APP_TIMEZONE=Asia/Kolkata \
ADMIN_USERNAME=admin \
AI_MODEL=qwen3:4b \
NONINTERACTIVE=1 \
curl -fsSL https://raw.githubusercontent.com/binesheb/google-review-autoreply/main/install.sh | sudo -E bash
```

On first install, `ADMIN_PASSWORD` must be provided securely and is converted into a PBKDF2 password hash. Do not place passwords in shell history or public automation logs.

## Persistent data

Docker volumes preserve:

- PostgreSQL data
- Qdrant data
- Ollama model data

The installer preserves `.env` during upgrades.

## Upgrade

Run the installer again or pull the repository and run:

```bash
review-platform up -d --build
```

The application code is replaced while persistent volumes and `.env` remain.

## Service operations

```bash
review-platform ps
review-platform logs -f api
review-platform restart
review-platform down
review-platform up -d
```

## Security

The default deployment is intended for controlled networks until HTTPS and production identity controls are configured. Do not expose the raw application port directly to the public internet without a reverse proxy, TLS, firewall policy and stronger authentication controls.

## Safe publishing rollout

The default product starts with automation paused. Recommended progression:

```text
Configure
  ↓
Historical dry run
  ↓
Golden benchmark
  ↓
Shadow mode
  ↓
Human approval
  ↓
Limited auto-publish
```

## Recovery

Before production, add scheduled PostgreSQL backups and test restoration. Keep a known-good application version available for rollback.
