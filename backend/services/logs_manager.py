from pathlib import Path

LOG_DIR = Path("/data/icecast/logs")


def tail_log(log_name: str, lines: int = 200):
    path = LOG_DIR / log_name
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()[-lines:]
