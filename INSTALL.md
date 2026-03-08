# Icecast Control Center - Zero-Code VPS Installation

## 1) Connect to server
```bash
ssh root@YOUR_SERVER_IP
```

## 2) Clone and install
```bash
git clone <YOUR-REPO-URL> icecast-control-center
cd icecast-control-center
bash install.sh
```

The installer automatically:
- Builds Icecast-KH from source
- Configures `/usr/local/etc/icecast.xml`
- Creates `icecast.service`
- Installs and configures `nginx-extras`
- Starts dashboard backend + frontend containers

## 3) Use dashboard
Open `http://SERVER-IP:3000`.

You can now control:
- All Icecast config sections (with backup + xmllint validation)
- Mounts, relays, listener auth (htpasswd + URL auth)
- Nginx domain + SSL + Cloudflare mode + `nginx -t` / reload / restart
- Analytics (CPU, RAM, bandwidth, peaks, history, top mounts)

## 4) Maintenance
```bash
bash update.sh
bash uninstall.sh
```
