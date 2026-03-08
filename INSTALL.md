# Icecast Control Center - Zero-Code VPS Installation

## 1) Login to your VPS
Use SSH from your computer:
```bash
ssh root@YOUR_SERVER_IP
```
(Or a sudo user.)

## 2) Download project
```bash
git clone <YOUR-REPO-URL> icecast-control-center
cd icecast-control-center
```

## 3) Run automatic install
```bash
bash install.sh
```

The installer automatically:
- Runs `apt update` and upgrades packages
- Installs Docker, Python, Node, xmllint
- Builds **Icecast-KH from source** (`/usr/local/bin/icecast`)
- Creates Icecast config: `/usr/local/etc/icecast.xml`
- Creates Icecast systemd service: `/etc/systemd/system/icecast.service`
- Installs `nginx-extras` and configures reverse proxy
- Builds and starts dashboard containers

It asks you for:
- Dashboard admin username/password
- Primary domain (example: `radio.example.com`)
- Icecast source/admin passwords

## 4) Open your dashboard
- Dashboard: `http://SERVER-IP:3000`
- Stream URL (proxy): `http://YOUR-DOMAIN`
- Direct Icecast: `http://SERVER-IP:8000`

## 5) Manage domain + SSL from UI
In the dashboard, open **Domain & SSL Control**:
- Set primary domain
- Enable HTTPS
- Select SSL mode (Cloudflare / Let's Encrypt / Custom)
- Reload/restart nginx
- Run nginx config test (`nginx -t`)

## 6) Update or remove
Update:
```bash
bash update.sh
```
Uninstall:
```bash
bash uninstall.sh
```
