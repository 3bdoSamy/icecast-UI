#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Verifying installer files in: $(pwd)"

for f in install.sh update.sh uninstall.sh; do
  if [ ! -f "$f" ]; then
    echo "[ERROR] Missing $f"
    exit 1
  fi
  perl -pi -e 's/\r$//' "$f"
  if [ "$f" = "install.sh" ]; then
    sed -i '1s/^\xEF\xBB\xBF//' "$f"
  fi
  chmod +x "$f"
  if ! bash -n "$f"; then
    echo "[ERROR] Bash syntax failed for $f"
    exit 1
  fi
done

echo "[OK] Shell syntax checks passed."

echo "[INFO] Compose detection:"
if command -v docker-compose >/dev/null 2>&1; then
  echo "[OK] docker-compose found at $(command -v docker-compose)"
else
  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    echo "[OK] docker compose (plugin) available"
  else
    echo "[ERROR] Neither docker-compose nor docker compose is available."
    echo "       Install one of them before running install.sh"
    exit 1
  fi
fi

echo "[DONE] Preflight checks are good. You can run: sudo -E bash ./install.sh"
