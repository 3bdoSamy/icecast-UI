# Icecast Control Center

Production-ready control panel stack for managing Icecast from a web UI (FastAPI + Next.js + Docker).

## Run locally
```bash
docker compose --env-file .env up -d --build
```

## Key features included
- JWT authentication with roles scaffold (Admin/Operator/Viewer)
- XML config editing and xmllint validation
- Icecast runtime controls (start/stop/restart)
- Admin endpoint integrations (list mounts / kill source)
- Realtime dashboard updates with WebSockets every 2 seconds
- Log tail endpoints
- Automated VPS install/update/uninstall scripts
