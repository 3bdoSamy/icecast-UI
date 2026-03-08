#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="/opt/icecast-control-center"
cd "$PROJECT_DIR"
sudo git pull || true
sudo docker compose --env-file .env build
sudo docker compose --env-file .env up -d
sudo systemctl restart icecast-control-center.service
echo "Update complete."
