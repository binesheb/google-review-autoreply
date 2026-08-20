#!/usr/bin/env sh
set -eu

# Safe in-place updater for a Git checkout plus its Docker Compose deployment.
# Intended to be called manually or by a scheduler from the repository root.

REPO_DIR="${REPO_DIR:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
BRANCH="${UPDATE_BRANCH:-main}"

cd "$REPO_DIR"

if [ -n "$(git status --porcelain)" ]; then
  echo "Refusing to update: the working tree has local changes."
  exit 1
fi

git fetch origin "$BRANCH"
git merge --ff-only "origin/$BRANCH"

docker compose config -q
docker compose pull
docker compose up -d --build --remove-orphans

echo "Update completed successfully. Review service status with: docker compose ps"
