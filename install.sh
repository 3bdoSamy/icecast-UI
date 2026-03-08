#!/usr/bin/env bash
[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"
set -euo pipefail

PROJECT_DIR="/opt/icecast-control-center"
ICECAST_SRC_DIR="/usr/local/src/icecast-kh"
ICECAST_BIN="/usr/local/bin/icecast"
ICECAST_CONF="/usr/local/etc/icecast.xml"
ICECAST_SERVICE="/etc/systemd/system/icecast.service"
CONTROL_SERVICE="/etc/systemd/system/icecast-control-center.service"
NGINX_CONF="/etc/nginx/conf.d/icecast.conf"

ARCH="$(uname -m)"
case "$ARCH" in
  x86_64|amd64)
    PLATFORM="amd64"
    ;;
  aarch64|arm64)
    PLATFORM="arm64"
    ;;
  *)
    PLATFORM="unknown"
    echo "[WARN] Unrecognized architecture: $ARCH. Installer will continue."
    ;;
esac

if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
    COMPOSE_EXEC="/usr/bin/docker-compose"
else
    COMPOSE="docker compose"
    COMPOSE_EXEC="/usr/bin/docker compose"
fi

run_compose() {
  eval "$COMPOSE $*"
}

check_resources() {
  local mem_mb disk_mb
  mem_mb=$(free -m | awk '/^Mem:/{print $2}')
  disk_mb=$(df -Pm / | awk 'NR==2{print $4}')
  if [ "$mem_mb" -lt 900 ]; then
    echo "[ERROR] Low memory detected (<900MB). Minimum recommended: 1GB RAM."; exit 1
  fi
  if [ "$disk_mb" -lt 4096 ]; then
    echo "[ERROR] Low disk space detected (<4GB free)."; exit 1
  fi
}

install_pkg() {
  local pkg="$1"
  dpkg -s "$pkg" >/dev/null 2>&1 || apt-get install -y "$pkg"
}

ensure_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker not found. Installing via official script (get.docker.com)..."
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sh /tmp/get-docker.sh
  fi

  install_pkg docker-compose

  if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
    COMPOSE_EXEC="/usr/bin/docker-compose"
  else
    COMPOSE="docker compose"
    COMPOSE_EXEC="/usr/bin/docker compose"
  fi
}

install_icecast_kh() {
  if [ -x "$ICECAST_BIN" ]; then
    echo "Icecast-KH binary exists at $ICECAST_BIN, skipping source build."
    return
  fi

  echo "Installing Icecast-KH build dependencies for $PLATFORM..."
  for pkg in     build-essential     libxml2-dev     libxslt1-dev     libssl-dev     libcurl4-openssl-dev     libvorbis-dev     libtheora-dev     libspeex-dev     libogg-dev     autoconf     automake     libtool     pkg-config     git
  do
  for pkg in build-essential libxml2-dev libxslt1-dev libssl-dev libcurl4-openssl-dev libvorbis-dev libtheora-dev libspeex-dev libogg-dev autoconf automake libtool pkg-config git; do
  echo "Installing Icecast-KH build dependencies..."
  for pkg in build-essential libxml2-dev libxslt1-dev libssl-dev libcurl4-openssl-dev libvorbis-dev libtheora-dev libspeex-dev libogg-dev pkg-config git autoconf automake libtool; do
    install_pkg "$pkg"
  done

  rm -rf "$ICECAST_SRC_DIR"
  git clone https://github.com/karlheyes/icecast-kh.git "$ICECAST_SRC_DIR"
  cd "$ICECAST_SRC_DIR"
  libtoolize --force
  aclocal
  autoheader
  autoconf
  automake --add-missing
  ./autogen.sh
  ./configure
  make -j"$(nproc)"
  make install
}

# Keep function declaration plain bash to avoid parser issues on strict environments
setup_icecast_service() {
  id -u icecast >/dev/null 2>&1 || useradd --system --home /var/lib/icecast --shell /usr/sbin/nologin icecast
  mkdir -p /var/log/icecast /var/lib/icecast /usr/local/etc /etc/icecast/backups
  chown -R icecast:icecast /var/log/icecast /var/lib/icecast /etc/icecast/backups

  if [ ! -f "$ICECAST_CONF" ]; then
    cp "$PROJECT_DIR/config/icecast.xml" "$ICECAST_CONF"
  fi

  sed -i "s|\${ICECAST_SOURCE_PASSWORD}|$ICECAST_SOURCE_PASSWORD|g; s|\${ICECAST_ADMIN_USER}|admin|g; s|\${ICECAST_ADMIN_PASSWORD}|$ICECAST_ADMIN_PASSWORD|g; s|\${ICECAST_RELAY_PASSWORD}|$ICECAST_RELAY_PASSWORD|g; s|\${SERVER_HOSTNAME}|$SERVER_HOSTNAME|g" "$ICECAST_CONF"

  cat > "$ICECAST_SERVICE" <<SERVICE
[Unit]
Description=Icecast-KH Streaming Server
After=network.target

[Service]
User=icecast
Group=icecast
ExecStart=/usr/local/bin/icecast -c /usr/local/etc/icecast.xml
Restart=always
RestartSec=3
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
SERVICE

  systemctl daemon-reload
  systemctl enable icecast --now
}

setup_nginx() {
  install_pkg nginx-extras
  install_pkg certbot
  install_pkg python3-certbot-nginx

  SERVER_HOSTNAME=${SERVER_HOSTNAME:-_}

  mkdir -p /etc/nginx/conf.d "$PROJECT_DIR/data/control/templates"
  cp "$PROJECT_DIR/config/templates/icecast.conf.tpl" "$PROJECT_DIR/data/control/templates/icecast.conf.tpl"

  cat > "$NGINX_CONF" <<CONF
server {
    listen 80;
    server_name $SERVER_HOSTNAME;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_set_header Accept-Encoding "";

        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header CF-Connecting-IP \$http_cf_connecting_ip;

        sub_filter_once off;
        sub_filter ':8000/' '/';
        sub_filter '@localhost' '@$SERVER_HOSTNAME';
        sub_filter 'localhost' '$SERVER_HOSTNAME';

        more_clear_headers Server;
        more_clear_headers X-Powered-By;
        more_set_headers "Cache-Control: no-store";
    }
}
CONF

  systemctl enable nginx --now
  if nginx -t; then
    systemctl reload nginx
  else
    echo "[WARN] nginx -t failed. Continuing installation. Review nginx config manually."
  fi
  nginx -t
  systemctl enable nginx --now
  systemctl reload nginx
}

setup_control_stack() {
  if [ -d "$PROJECT_DIR/.git" ]; then
    git -C "$PROJECT_DIR" pull || true
  fi

  cat > "$PROJECT_DIR/.env" <<ENV
ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_PASSWORD=$ADMIN_PASSWORD
SERVER_HOSTNAME=$SERVER_HOSTNAME
ICECAST_SOURCE_PASSWORD=$ICECAST_SOURCE_PASSWORD
ICECAST_ADMIN_USER=admin
ICECAST_ADMIN_PASSWORD=$ICECAST_ADMIN_PASSWORD
ICECAST_RELAY_PASSWORD=$ICECAST_RELAY_PASSWORD
JWT_SECRET=$JWT_SECRET
ENV

  mkdir -p "$PROJECT_DIR/data/control" "$PROJECT_DIR/data/icecast/logs"

  if ss -ltn '( sport = :3000 or sport = :8001 )' | grep -q LISTEN; then
    echo "[ERROR] Port conflict detected on 3000/8001."; exit 1
  fi

  run_compose "--env-file '$PROJECT_DIR/.env' -f '$PROJECT_DIR/docker-compose.yml' up -d --build"
  docker compose --env-file "$PROJECT_DIR/.env" -f "$PROJECT_DIR/docker-compose.yml" up -d --build

  cat > "$CONTROL_SERVICE" <<SERVICE
[Unit]
Description=Icecast Control Center
After=docker.service nginx.service icecast.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=$PROJECT_DIR
RemainAfterExit=true
ExecStart=$COMPOSE_EXEC --env-file .env up -d
ExecStop=$COMPOSE_EXEC --env-file .env down
ExecStart=/usr/bin/docker compose --env-file .env up -d
ExecStop=/usr/bin/docker compose --env-file .env down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
SERVICE

  systemctl daemon-reload
  systemctl enable icecast-control-center --now
}

echo "Updating apt cache for architecture: $ARCH ($PLATFORM)"
echo "Updating apt cache..."
apt update
apt upgrade -y
check_resources

for pkg in curl nodejs npm python3 python3-pip git libxml2-utils; do
  install_pkg "$pkg"
done

ensure_docker
for pkg in curl docker.io docker-compose-plugin nodejs npm python3 python3-pip git libxml2-utils; do
  install_pkg "$pkg"
done
systemctl enable docker --now

read -rp "Dashboard admin username: " ADMIN_USERNAME
read -rsp "Dashboard admin password: " ADMIN_PASSWORD; echo
read -rp "Primary domain/hostname (optional, press Enter to skip): " SERVER_HOSTNAME
SERVER_HOSTNAME=${SERVER_HOSTNAME:-_}
read -rp "Primary domain/hostname (example radio.example.com): " SERVER_HOSTNAME
read -rp "Icecast source password: " ICECAST_SOURCE_PASSWORD
read -rp "Icecast admin password: " ICECAST_ADMIN_PASSWORD
JWT_SECRET=$(openssl rand -hex 32)
ICECAST_RELAY_PASSWORD=$(openssl rand -hex 8)

if [ ! -d "$PROJECT_DIR" ]; then
  mkdir -p "$PROJECT_DIR"
  cp -R . "$PROJECT_DIR"
fi

install_icecast_kh
setup_icecast_service
setup_nginx
setup_control_stack

SERVER_IP=$(hostname -I | awk '{print $1}')
echo "\nInstallation complete"
echo "Dashboard URL: http://$SERVER_IP:3000"
echo "Icecast URL (via nginx): http://$SERVER_HOSTNAME"
echo "Direct Icecast URL: http://$SERVER_IP:8000"
echo "Admin username: $ADMIN_USERNAME"
