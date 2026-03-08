#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/opt/icecast-control-center"
SERVICE_FILE="/etc/systemd/system/icecast-control-center.service"

check_resources() {
  local mem_mb disk_mb
  mem_mb=$(free -m | awk '/^Mem:/{print $2}')
  disk_mb=$(df -Pm / | awk 'NR==2{print $4}')
  if [ "$mem_mb" -lt 900 ]; then
    echo "[ERROR] Low memory detected (<900MB). Please upgrade VPS RAM to at least 1GB."
    exit 1
  fi
  if [ "$disk_mb" -lt 4096 ]; then
    echo "[ERROR] Low disk space detected (<4GB free). Free disk space and retry."
    exit 1
  fi
}

install_pkg() {
  local pkg="$1"
  dpkg -s "$pkg" >/dev/null 2>&1 || sudo apt-get install -y "$pkg"
}

echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y
check_resources

for pkg in git curl docker.io docker-compose-plugin nodejs npm python3 python3-pip libxml2-utils; do
  install_pkg "$pkg"
done

sudo systemctl enable docker --now

read -rp "Dashboard admin username: " ADMIN_USERNAME
read -rsp "Dashboard admin password: " ADMIN_PASSWORD; echo
read -rp "Server hostname (IP/domain): " SERVER_HOSTNAME
read -rp "Icecast source password: " ICECAST_SOURCE_PASSWORD
read -rp "Icecast admin password: " ICECAST_ADMIN_PASSWORD

JWT_SECRET=$(openssl rand -hex 32)
ICECAST_ADMIN_USER="admin"
ICECAST_RELAY_PASSWORD=$(openssl rand -hex 8)

if [ -d "$PROJECT_DIR" ]; then
  echo "Existing install found, pulling latest..."
  sudo git -C "$PROJECT_DIR" pull
else
  sudo mkdir -p "$PROJECT_DIR"
  sudo cp -R . "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"
sudo mkdir -p data/icecast/logs

cat <<ENV | sudo tee .env >/dev/null
ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_PASSWORD=$ADMIN_PASSWORD
SERVER_HOSTNAME=$SERVER_HOSTNAME
ICECAST_SOURCE_PASSWORD=$ICECAST_SOURCE_PASSWORD
ICECAST_ADMIN_USER=$ICECAST_ADMIN_USER
ICECAST_ADMIN_PASSWORD=$ICECAST_ADMIN_PASSWORD
ICECAST_RELAY_PASSWORD=$ICECAST_RELAY_PASSWORD
JWT_SECRET=$JWT_SECRET
ENV

sudo cp config/icecast.xml data/icecast/icecast.xml
sudo sed -i "s|\${ICECAST_SOURCE_PASSWORD}|$ICECAST_SOURCE_PASSWORD|g; s|\${ICECAST_ADMIN_USER}|$ICECAST_ADMIN_USER|g; s|\${ICECAST_ADMIN_PASSWORD}|$ICECAST_ADMIN_PASSWORD|g; s|\${ICECAST_RELAY_PASSWORD}|$ICECAST_RELAY_PASSWORD|g; s|\${SERVER_HOSTNAME}|$SERVER_HOSTNAME|g" data/icecast/icecast.xml

if sudo ss -ltn '( sport = :80 or sport = :3000 or sport = :8000 or sport = :8001 )' | grep -q LISTEN; then
  echo "[ERROR] Port conflict detected on 80/3000/8000/8001. Stop conflicting services and retry."
  exit 1
fi

sudo docker compose --env-file .env up -d --build

cat <<SERVICE | sudo tee "$SERVICE_FILE" >/dev/null
[Unit]
Description=Icecast Control Center
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=$PROJECT_DIR
RemainAfterExit=true
ExecStart=/usr/bin/docker compose --env-file .env up -d
ExecStop=/usr/bin/docker compose --env-file .env down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable icecast-control-center.service --now

SERVER_IP=$(hostname -I | awk '{print $1}')
echo "Installation complete!"
echo "Dashboard URL: http://$SERVER_IP:3000"
echo "Icecast URL: http://$SERVER_IP:8000"
echo "Admin username: $ADMIN_USERNAME"
echo "Admin password: (as entered)"
