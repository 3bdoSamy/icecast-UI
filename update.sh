#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="/opt/icecast-control-center"

compose() {
  if command -v docker-compose >/dev/null 2>&1; then
    docker-compose "$@"
  else
    docker compose "$@"
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
