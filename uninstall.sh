#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="/opt/icecast-control-center"
if [ -d "$PROJECT_DIR" ]; then
  cd "$PROJECT_DIR"
  docker compose --env-file .env down -v --rmi all || true
fi
systemctl disable --now icecast-control-center || true
systemctl disable --now icecast || true
rm -f /etc/systemd/system/icecast-control-center.service /etc/systemd/system/icecast.service
systemctl daemon-reload
rm -f /etc/nginx/conf.d/icecast.conf
systemctl reload nginx || true
rm -rf "$PROJECT_DIR" /usr/local/src/icecast-kh
SERVICE_FILE="/etc/systemd/system/icecast-control-center.service"
if [ -d "$PROJECT_DIR" ]; then
  cd "$PROJECT_DIR"
  sudo docker compose --env-file .env down -v --rmi all || true
fi
sudo systemctl disable --now icecast-control-center.service || true
sudo rm -f "$SERVICE_FILE"
sudo systemctl daemon-reload
sudo rm -rf "$PROJECT_DIR"
echo "Icecast Control Center removed."
