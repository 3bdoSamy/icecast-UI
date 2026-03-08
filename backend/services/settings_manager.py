import json
from pathlib import Path

SETTINGS_PATH = Path('/data/control/dashboard_settings.json')
DEFAULTS = {'ws_interval_seconds': 2}


def get_settings() -> dict:
    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(DEFAULTS, indent=2), encoding='utf-8')
        return DEFAULTS.copy()
    data = json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))
    return {**DEFAULTS, **data}


def set_ws_interval(seconds: int) -> dict:
    settings = get_settings()
    settings['ws_interval_seconds'] = max(1, min(30, int(seconds)))
    SETTINGS_PATH.write_text(json.dumps(settings, indent=2), encoding='utf-8')
    return settings
