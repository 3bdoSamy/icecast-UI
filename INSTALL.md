# Icecast Control Center - Zero-Code VPS Installation

## 1) Connect to server
```bash
ssh root@YOUR_SERVER_IP
```

## 2) Clean old copy (important)
```bash
cd ~/Desktop || cd ~
rm -rf icecast-control-center
```

## 3) Clone fresh and install
```bash
git clone https://github.com/3bdoSamy/icecast-UI.git icecast-control-center
cd icecast-control-center

# normalize scripts and verify syntax
apt-get update
apt-get install -y dos2unix
dos2unix install.sh update.sh uninstall.sh
perl -pi -e 's/\r$//' install.sh update.sh uninstall.sh
sed -i '1s/^\xEF\xBB\xBF//' install.sh
chmod +x install.sh update.sh uninstall.sh

./verify-install.sh

# run installer
sudo -E bash ./install.sh
```

The installer automatically:
- Builds Icecast-KH from source
- Configures `/usr/local/etc/icecast.xml`
- Creates `icecast.service`
- Installs and configures `nginx-extras`
- Starts dashboard backend + frontend containers

## 4) Use dashboard
Open `http://SERVER-IP:3000`.

## 5) Maintenance
```bash
bash update.sh
bash uninstall.sh
```

## Troubleshooting
If you ever see syntax errors near `x86_64|amd64)` or unexpected EOF, your local copy is stale/corrupted. Re-run steps 2 and 3 exactly to fetch a clean copy.


If `git checkout feature/install-hotfix-no-case` fails, skip that step and install directly from the default branch; that branch may not exist in your clone or remote.


## Fast sanity check before install
Run this inside the cloned repo:
```bash
head -n 20 install.sh | nl -ba
bash -n install.sh
```
You should see an `INSTALLER_VERSION` line near the top and no syntax output from `bash -n`.

## If your clone still looks old
Force-refresh the scripts from the default branch:
```bash
cd ~/Desktop/icecast-control-center
git checkout -- install.sh update.sh uninstall.sh
git pull --ff-only
```


If preflight fails, do not run installer yet; fix the reported issue first.
