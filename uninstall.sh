#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="/opt/icecast-control-center"

compose() {
  if command -v docker-compose >/dev/null 2>&1; then
    docker-compose "$@"
  else
    if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
      docker compose "$@"
    else
      echo "[ERROR] Could not find a working Docker Compose command (docker-compose or docker compose)." >&2
      exit 1
    fi
  fi
}

if [ -d "$PROJECT_DIR" ]; then
  cd "$PROJECT_DIR"
  compose --env-file .env down -v --rmi all || true
fi
systemctl disable --now icecast-control-center || true
systemctl disable --now icecast || true
rm -f /etc/systemd/system/icecast-control-center.service /etc/systemd/system/icecast.service
systemctl daemon-reload
rm -f /etc/nginx/conf.d/icecast.conf
systemctl reload nginx || true
rm -rf "$PROJECT_DIR" /usr/local/src/icecast-kh
echo "Icecast Control Center removed."
