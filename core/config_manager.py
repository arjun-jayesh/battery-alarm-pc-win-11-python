"""
Config Manager Module
Handles persistence of user settings (target %, alarm enabled) via JSON.
"""

import json
import os
import sys

_DEFAULTS = {
    "target_percent": 80,
    "alarm_enabled": True,
    "start_on_startup": False,
}


def _config_path() -> str:
    """Return the path to config.json next to the executable or script."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "config.json")


def load_config() -> dict:
    """Load config from disk, returning defaults on any error."""
    path = _config_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults so new keys are always present
        merged = {**_DEFAULTS, **data}
        return merged
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)


def save_config(config: dict):
    """Persist the config dict to disk."""
    path = _config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except OSError:
        pass  # Silently ignore write errors (e.g. read-only dir)
