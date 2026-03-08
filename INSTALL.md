# Icecast Control Center - Beginner Installation Guide

## 1) Connect to your VPS
Use your VPS provider terminal or SSH client and log in as a sudo user.

## 2) Download project
```bash
git clone <YOUR-REPO-URL> icecast-control-center
cd icecast-control-center
```

## 3) Run automatic installer
```bash
bash install.sh
```
Answer the on-screen questions:
- Dashboard admin username
- Dashboard admin password
- Server hostname/IP
- Icecast source password
- Icecast admin password

The installer automatically:
- Updates Ubuntu
- Installs Docker and tools
- Builds containers
- Starts services
- Creates auto-start service on reboot

## 4) Open dashboard
After install, open:
- Dashboard: `http://YOUR-SERVER-IP:3000`
- Icecast stream server: `http://YOUR-SERVER-IP:8000`

## 5) Login
Use your dashboard username/password you entered during installation.

## 6) Daily operations
- Start/stop/restart Icecast from Runtime API controls
- Edit XML configuration in Configuration endpoints/UI extension
- Monitor listeners/sources on dashboard charts in real-time
- View logs from Logs section

## 7) Update system
```bash
bash update.sh
```

## 8) Uninstall system
```bash
bash uninstall.sh
```
