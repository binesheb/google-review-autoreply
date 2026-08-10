#!/usr/bin/env bash
set -Eeuo pipefail

INSTALL_DIR="/opt/jayalakshmi-review"
PORT="8000"

log() { printf '\n[Jayalakshmi Review] %s\n' "$*"; }
die() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

[[ "$(id -u)" -eq 0 ]] || die "Run as root: curl -fsSL https://raw.githubusercontent.com/binesheb/google-review-autoreply/main/install.sh | sudo bash"

command -v curl >/dev/null 2>&1 || die "curl is required. Install curl and run the installer again."
command -v tar >/dev/null 2>&1 || die "tar is required. Install tar and run the installer again."

. /etc/os-release

install_docker_debian() {
  log "Installing Docker Engine from Docker's official APT repository..."
  apt-get update
  apt-get install -y ca-certificates curl
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
    *) die "Docker Compose is not installed. Install Docker Engine + Compose for this Linux distribution, then rerun the installer." ;;
  esac
fi

log "Preparing installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
ARCHIVE="$TMP_DIR/review-platform.tar.gz"

log "Downloading the application from GitHub (main)..."
curl -fL --retry 3 --retry-delay 2 "https://github.com/binesheb/google-review-autoreply/archive/refs/heads/main.tar.gz" -o "$ARCHIVE"

rm -rf "$INSTALL_DIR"/*
tar -xzf "$ARCHIVE" -C "$TMP_DIR"
SOURCE_DIR="$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d -name 'google-review-autoreply-*' | head -n 1)"
[[ -n "$SOURCE_DIR" ]] || die "Downloaded repository archive could not be unpacked."
cp -a "$SOURCE_DIR"/. "$INSTALL_DIR"/

cd "$INSTALL_DIR"

if [[ ! -f .env ]]; then
  cp .env.example .env
  SECRET="$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 48 || true)"
  if [[ -n "$SECRET" ]]; then
    sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET/" .env
  fi
fi

# Preserve existing configuration and database volumes when the installer is rerun.
if grep -q '^APP_PORT=' .env; then
  sed -i "s/^APP_PORT=.*/APP_PORT=$PORT/" .env
else
  printf '\nAPP_PORT=%s\n' "$PORT" >> .env
fi

log "Building and starting the server..."
docker compose up -d --build --remove-orphans

log "Waiting for the API to become healthy..."
for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:${PORT}/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if ! curl -fsS "http://127.0.0.1:${PORT}/api/health" >/dev/null 2>&1; then
  docker compose ps
  docker compose logs --tail=80 api || true
  die "The API did not become healthy."
fi

cat > /usr/local/bin/jayalakshmi-review <<'EOF'
#!/usr/bin/env bash
set -e
cd /opt/jayalakshmi-review
exec docker compose "$@"
EOF
chmod +x /usr/local/bin/jayalakshmi-review

IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
log "Installation complete."
echo "Dashboard: http://${IP:-localhost}:${PORT}/"
echo "API docs:  http://${IP:-localhost}:${PORT}/docs"
echo "Health:    http://${IP:-localhost}:${PORT}/api/health"
echo "Install:   $INSTALL_DIR"
echo "Management: jayalakshmi-review ps | logs | pull | up -d"
