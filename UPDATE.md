# Updating Review Intelligence Platform

This deployment is designed to be upgraded without replacing persistent PostgreSQL, Qdrant or Ollama data.

## Automatic update

The repository includes `scripts/update.sh`. Automatic updates are restricted to `origin/main`; the script refuses local changes, non-`main` checkouts and diverged history, then performs a fast-forward-only update. It validates the Compose configuration, refreshes container images/build dependencies, and recreates the stack without touching persistent volumes. If deployment validation fails, it restores the previous repository revision and attempts to bring the known-good stack back.

For a managed deployment, install the included systemd units:

```bash
sudo install -m 0644 deploy/review-intelligence-update.service /etc/systemd/system/
sudo install -m 0644 deploy/review-intelligence-update.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now review-intelligence-update.timer
```

The timer runs daily with a randomized delay. Disable it when updates must be approved manually.

Database migrations should be applied before exposing a new application version when the release includes schema changes:

```bash
docker compose run --rm api alembic upgrade head
```

Automatic upgrades should run with backups and monitoring in place.

## Manual update

1. Back up PostgreSQL and any other required persistent data.
2. Review the changes on `origin/main` and any breaking-change instructions.
3. From a clean checkout on `main`, run:

```bash
sh scripts/update.sh
```

The updater stops if the working tree contains local changes, the checkout is not `main`, history has diverged, or the update cannot be fast-forwarded. Docker Compose refreshes declared images/build dependencies as part of the update.

4. Apply Alembic migrations when required:

```bash
docker compose run --rm api alembic upgrade head
```

5. Verify the dashboard, API health, review ingestion and publication policy before enabling broader automation.

## Rollback

The updater automatically restores the previous repository revision when validation or deployment fails. For a manual rollback, return to a known-good commit and restart the stack. Do not delete persistent volumes as part of rollback unless restoring from a verified backup.

## Safety boundary

An application update must not automatically change business publication policy. After every upgrade, review `AUTO_PUBLISH_ENABLED`, approval rules and integrations before allowing replies to be published automatically.
