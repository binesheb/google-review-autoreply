#!/usr/bin/env bash
set -Eeuo pipefail

PRODUCT="Review Intelligence Platform"
DEFAULT_INSTALL_DIR="/opt/review-intelligence"
DEFAULT_PORT="8000"
DEFAULT_TIMEZONE="UTC"
DEFAULT_MODEL="qwen3:4b"

log() { printf '\n[Review Intelligence] %s\n' "$*"; }
die() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

[[ "$(id -u)" -eq 0 ]] || die "Run as root: curl -fsSL https://raw.githubusercontent.com/binesheb/google-review-autoreply/main/install.sh | sudo bash"
command -v curl >/dev/null 2>&1 || die "curl is required."
command -v tar >/dev/null 2>&1 || die "tar is required."

. /etc/os-release

install_docker_debian() {
  log "Installing Docker Engine and Compose from Docker's official repository..."
  apt-get update
  apt-get install -y ca-certificates curl gnupg python3
  install -m 0755 -d /etc/apt/keyrings

  if [[ "$ID" == "ubuntu" ]]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    cat >/etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${UBUNTU_CODENAME:-$VERSION_CODENAME}
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
  elif [[ "$ID" == "debian" ]]; then
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    cat >/etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $VERSION_CODENAME
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
  else
    return 1
  fi

  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable --now docker
}

if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  case "$ID" in
    ubuntu|debian) install_docker_debian || die "Docker installation failed." ;;
    *) die "This installer currently supports Ubuntu and Debian. Install Docker Engine + Compose for another distribution, then rerun." ;;
  esac
fi

# First-run configuration. Existing .env values are preserved on upgrades.
INSTALL_DIR="${INSTALL_DIR:-$DEFAULT_INSTALL_DIR}"
APP_PORT="${APP_PORT:-$DEFAULT_PORT}"
APP_TIMEZONE="${APP_TIMEZONE:-$DEFAULT_TIMEZONE}"
AI_MODEL="${AI_MODEL:-$DEFAULT_MODEL}"
APP_NAME="${APP_NAME:-$PRODUCT}"
ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
AUTO_PUBLISH_ENABLED="${AUTO_PUBLISH_ENABLED:-false}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
ARCHIVE="$TMP_DIR/review-platform.tar.gz"

log "Downloading the current product from GitHub main..."
curl -fL --retry 3 --retry-delay 2 "https://github.com/binesheb/google-review-autoreply/archive/refs/heads/main.tar.gz" -o "$ARCHIVE"
tar -xzf "$ARCHIVE" -C "$TMP_DIR"
SOURCE_DIR="$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d -name 'google-review-autoreply-*' | head -n 1)"
[[ -n "$SOURCE_DIR" ]] || die "Repository archive could not be unpacked."

mkdir -p "$INSTALL_DIR"
if [[ -f "$INSTALL_DIR/.env" ]]; then
  log "Existing installation detected. Preserving configuration and Docker volumes."
  # Load non-secret values as defaults for the interactive prompts.
  set +u
  source "$INSTALL_DIR/.env" || true
  set -u
  APP_NAME="${APP_NAME:-$PRODUCT}"
  APP_PORT="${APP_PORT:-$DEFAULT_PORT}"
  APP_TIMEZONE="${APP_TIMEZONE:-$DEFAULT_TIMEZONE}"
  AI_MODEL="${AI_MODEL:-$DEFAULT_MODEL}"
  ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
  AUTO_PUBLISH_ENABLED="${AUTO_PUBLISH_ENABLED:-false}"
fi

if [[ "${NONINTERACTIVE:-0}" != "1" ]]; then
  printf '\n%s\n' "Initial setup (press Enter to keep the value in brackets)"
  read -r -p "Product name [$APP_NAME]: " v; APP_NAME="${v:-$APP_NAME}"
  read -r -p "Admin username [$ADMIN_USERNAME]: " v; ADMIN_USERNAME="${v:-$ADMIN_USERNAME}"
  if [[ -z "${ADMIN_PASSWORD_HASH:-}" ]]; then
    while true; do
      read -r -s -p "Admin password: " p1; echo
      read -r -s -p "Confirm admin password: " p2; echo
      [[ "$p1" == "$p2" && -n "$p1" ]] && break
      echo "Passwords do not match. Try again."
    done
    ADMIN_PASSWORD="$p1"
  else
    ADMIN_PASSWORD=""
  fi
  read -r -p "Web port [$APP_PORT]: " v; APP_PORT="${v:-$APP_PORT}"
  read -r -p "Timezone [$APP_TIMEZONE]: " v; APP_TIMEZONE="${v:-$APP_TIMEZONE}"
  read -r -p "Local AI model [$AI_MODEL]: " v; AI_MODEL="${v:-$AI_MODEL}"
  read -r -p "Enable automatic publishing now? [y/N]: " v
  [[ "${v:-N}" =~ ^[Yy]$ ]] && AUTO_PUBLISH_ENABLED=true || AUTO_PUBLISH_ENABLED=false
  read -r -p "Installation directory [$INSTALL_DIR]: " v; INSTALL_DIR="${v:-$INSTALL_DIR}"
fi

# Generate secrets only when they do not already exist.
if [[ -z "${SECRET_KEY:-}" ]]; then
  SECRET_KEY="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
fi
if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
  POSTGRES_PASSWORD="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
)"
fi
if [[ -z "${ADMIN_PASSWORD_HASH:-}" ]]; then
  [[ -n "${ADMIN_PASSWORD:-}" ]] || die "An admin password is required on first install."
  export ADMIN_PASSWORD
  ADMIN_PASSWORD_HASH="$(python3 - <<'PY'
import hashlib, os
password=os.environ['ADMIN_PASSWORD'].encode()
salt=os.urandom(16).hex()
digest=hashlib.pbkdf2_hmac('sha256', password, salt.encode(), 210000).hex()
print(f'pbkdf2_sha256$210000${salt}${digest}')
PY
)"
  unset ADMIN_PASSWORD
fi

log "Installing application files into $INSTALL_DIR"
# Preserve .env while replacing application code.
find "$INSTALL_DIR" -mindepth 1 -maxdepth 1 ! -name .env -exec rm -rf {} +
cp -a "$SOURCE_DIR"/. "$INSTALL_DIR"/

cat >"$INSTALL_DIR/.env" <<EOF
APP_NAME=$(printf '%s' "$APP_NAME" | sed 's/[&|]/_/g')
APP_ENV=production
APP_PORT=$APP_PORT
APP_TIMEZONE=$APP_TIMEZONE
ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_PASSWORD_HASH=$ADMIN_PASSWORD_HASH
SECRET_KEY=$SECRET_KEY
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=review_platform
POSTGRES_USER=review_platform
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
QDRANT_URL=http://qdrant:6333
AI_BASE_URL=http://ollama:11434
AI_MODEL=$AI_MODEL
GOOGLE_ENABLED=false
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:$APP_PORT/api/google/oauth/callback
GOOGLE_ACCESS_TOKEN=
GOOGLE_ACCOUNT_ID=
AUTO_PUBLISH_ENABLED=$AUTO_PUBLISH_ENABLED
AUTOMATION_PAUSED=true
POLL_INTERVAL_MINUTES=10
DAILY_PUBLISH_LIMIT=25
LOG_LEVEL=INFO
EOF
chmod 600 "$INSTALL_DIR/.env"

cd "$INSTALL_DIR"
log "Building and starting the platform..."
docker compose up -d --build --remove-orphans

log "Waiting for the application..."
for _ in $(seq 1 90); do
  if curl -fsS "http://127.0.0.1:${APP_PORT}/api/health" >/dev/null 2>&1; then break; fi
  sleep 2
done
curl -fsS "http://127.0.0.1:${APP_PORT}/api/health" >/dev/null 2>&1 || { docker compose ps; docker compose logs --tail=100 api || true; die "The application did not become healthy."; }

cat >/usr/local/bin/review-platform <<EOF
#!/usr/bin/env bash
set -e
cd "$INSTALL_DIR"
exec docker compose "\$@"
EOF
chmod +x /usr/local/bin/review-platform

IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
log "Installation complete."
echo "Dashboard: http://${IP:-localhost}:${APP_PORT}/"
echo "API docs:  http://${IP:-localhost}:${APP_PORT}/docs"
echo "Health:    http://${IP:-localhost}:${APP_PORT}/api/health"
echo "Install:   $INSTALL_DIR"
echo "Commands:  review-platform ps | logs | up -d | down"
echo "Publishing: $AUTO_PUBLISH_ENABLED (automation remains PAUSED until enabled in the product)"
