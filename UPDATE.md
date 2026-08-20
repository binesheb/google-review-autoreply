# Updating Review Intelligence Platform

This deployment is designed to be upgraded without replacing persistent PostgreSQL, Qdrant or Ollama data.

## Automatic update

For a managed deployment, schedule the following command from a trusted administrator account. The command is intentionally explicit and only updates the checked-out repository and application containers:

```bash
cd /opt/review-intelligence
git fetch origin main
git merge --ff-only origin/main
docker compose pull
docker compose up -d --remove-orphans
```

`--ff-only` prevents the updater from silently overwriting local changes. If the checkout has diverged, resolve that state manually before continuing.

Database migrations should be applied before exposing a new application version when the release includes schema changes:

```bash
docker compose run --rm app alembic upgrade head
```

Use a systemd timer or another scheduler only when the server is dedicated to this deployment and the administrator accepts automatic application upgrades. Automatic upgrades should run with backups and monitoring in place.

## Manual update

1. Back up PostgreSQL and any other required persistent data.
2. Check the target release notes and breaking-change instructions.
3. From the installation directory, fetch the release tag:

```bash
git fetch --tags origin
git checkout <release-tag>
```

4. Pull/build the deployment and start it:

```bash
docker compose pull
docker compose up -d --build --remove-orphans
```

5. Apply Alembic migrations when required:

```bash
docker compose run --rm app alembic upgrade head
```

6. Verify the dashboard, API health, review ingestion and publication policy before enabling broader automation.

## Rollback

If a release fails validation, return to the previously known-good Git tag and restart the stack. Do not delete persistent volumes as part of rollback unless restoring from a verified backup.

## Safety boundary

An application update must not automatically change business publication policy. After every upgrade, review `AUTO_PUBLISH_ENABLED`, approval rules and integrations before allowing replies to be published automatically.
