# Icecast Control Center

Icecast Control Center is a production-oriented web control panel for Icecast with:
- FastAPI backend API + WebSockets
- Next.js dashboard UI
- Icecast-KH installed from source (`/usr/local/bin/icecast`)
- Host nginx-extras reverse proxy with domain + SSL controls

## Deployment
On Ubuntu 22.04/24.04:
```bash
bash install.sh
```

The installer will:
- Build/install Icecast-KH from source
- Create `/usr/local/etc/icecast.xml`
- Create and start `/etc/systemd/system/icecast.service`
- Install/configure `nginx-extras`
- Build/start dashboard containers

## Operations
- Update: `bash update.sh`
- Uninstall: `bash uninstall.sh`
