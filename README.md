# Icecast Control Center

Full control plane for Icecast / Icecast-KH with web UI + API.

## What is now covered
- Full XML section editing with backup + xmllint validation before apply:
  - Limits, Authentication, Directory, Server settings, Listen sockets, HTTP headers
  - Relays (master + specific mount), Mount defaults/settings, Paths, Logging, Security
- Missing options included: `burst-on-connect`, `header-timeout`, multi listen-sockets,
  `default-type`, `dump-file`, `intro`, `charset`, hidden mounts, `mp3-metadata-interval`,
  `relay-shoutcast-metadata`, `relays-on-demand`, alias paths, `logsize`, `logarchive`,
  `security/chroot`, `changeowner user/group`.
- Mount management CRUD for full mount config.
- Listener authentication:
  - htpasswd user management
  - URL auth endpoints (`mount_add`, `mount_remove`, `listener_add`, `listener_remove`, `stream_auth`)
- Stream token issuance endpoint.
- Analytics and monitoring: CPU, RAM, network bandwidth, listener peaks, historical listeners, top mounts, per-mount history.
- Nginx integration: domain management, SSL mode switching (Cloudflare / Let's Encrypt / custom), config generation, validation, reload/restart.

## Install (recommended)
```bash
git clone https://github.com/3bdoSamy/icecast-UI.git icecast-control-center
cd icecast-control-center
chmod +x install.sh update.sh uninstall.sh
bash -n install.sh && bash -n update.sh && bash -n uninstall.sh
sudo -E bash ./install.sh
```

If you previously cloned an old copy, remove it and clone again before installing.
## Install
```bash
bash install.sh
```
