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

cd "$PROJECT_DIR"
git pull || true
compose --env-file .env build
compose --env-file .env up -d
systemctl restart icecast-control-center
systemctl reload nginx
systemctl restart icecast
echo "Update complete."
