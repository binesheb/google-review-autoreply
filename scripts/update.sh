#!/usr/bin/env sh
set -eu

# Safe in-place updater for a Git checkout plus its Docker Compose deployment.
# Intended to be called manually or by a scheduler from the repository root.
# Automatic updates are intentionally restricted to origin/main.

REPO_DIR="${REPO_DIR:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
BRANCH="main"

cd "$REPO_DIR"

if [ -n "$(git status --porcelain)" ]; then
  echo "Refusing to update: the working tree has local changes."
  exit 1
fi

CURRENT_BRANCH="$(git branch --show-current)"
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
  echo "Refusing to update: automatic updates must run from $BRANCH, not ${CURRENT_BRANCH:-detached HEAD}."
  exit 1
fi

PREVIOUS_REVISION="$(git rev-parse HEAD)"
git fetch origin "$BRANCH"

if ! git merge-base --is-ancestor HEAD "origin/$BRANCH"; then
  echo "Refusing to update: local history has diverged from origin/$BRANCH."
  exit 1
fi

if [ "$PREVIOUS_REVISION" = "$(git rev-parse "origin/$BRANCH")" ]; then
  echo "Already up to date with origin/$BRANCH."
  exit 0
fi

git merge --ff-only "origin/$BRANCH"

if ! docker compose config -q || ! docker compose pull || ! docker compose up -d --build --remove-orphans; then
  echo "Update failed. Restoring repository revision $PREVIOUS_REVISION."
  git reset --hard "$PREVIOUS_REVISION"
  docker compose config -q && docker compose up -d --build --remove-orphans || true
  exit 1
fi

echo "Update completed successfully from origin/$BRANCH. Review service status with: docker compose ps"
