#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="/opt/icecast-control-center"
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
