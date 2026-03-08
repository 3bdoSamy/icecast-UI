import subprocess


def _run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {"ok": proc.returncode == 0, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}


def start_icecast():
    return _run(["systemctl", "start", "icecast"])


def stop_icecast():
    return _run(["systemctl", "stop", "icecast"])


def restart_icecast():
    return _run(["systemctl", "restart", "icecast"])


def reload_icecast():
    return _run(["systemctl", "reload", "icecast"])


def icecast_status():
    return _run(["systemctl", "status", "icecast", "--no-pager"])
import os
import subprocess

COMPOSE_FILE = os.getenv("COMPOSE_FILE", "/app/docker-compose.yml")


def run_compose(command: list[str]) -> dict:
    cmd = ["docker", "compose", "-f", COMPOSE_FILE, *command]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr}


def start_icecast():
    return run_compose(["up", "-d", "icecast"])


def stop_icecast():
    return run_compose(["stop", "icecast"])


def restart_icecast():
    return run_compose(["restart", "icecast"])


def reload_icecast():
    return run_compose(["restart", "icecast"])
