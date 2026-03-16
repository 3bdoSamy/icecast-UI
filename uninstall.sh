#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="/opt/icecast-control-center"

compose_down() {
  if [ ! -d "$PROJECT_DIR" ]; then
    return
  fi

  cd "$PROJECT_DIR"
  if command -v docker-compose >/dev/null 2>&1; then
    docker-compose --env-file .env down -v --rmi all || true
    return
  fi

  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    docker compose --env-file .env down -v --rmi all || true
    return
  fi

  echo "[WARN] Compose not found; skipping container teardown."
}

compose_down

systemctl disable --now icecast-control-center || true
systemctl disable --now icecast || true
rm -f /etc/systemd/system/icecast-control-center.service /etc/systemd/system/icecast.service
systemctl daemon-reload
rm -f /etc/nginx/conf.d/icecast.conf
systemctl reload nginx || true
rm -rf "$PROJECT_DIR" /usr/local/src/icecast-kh

echo "Icecast Control Center removed."
