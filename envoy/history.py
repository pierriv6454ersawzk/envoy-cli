"""Track per-key change history within a profile vault."""

import json
import time
from pathlib import Path
from typing import Optional

from envoy.profile import get_vault_dir


def _history_path(profile: str, base_dir: Optional[str] = None) -> Path:
    return get_vault_dir(base_dir) / f"{profile}.history.json"


def _read_history(profile: str, base_dir: Optional[str] = None) -> dict:
    p = _history_path(profile, base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_history(profile: str, data: dict, base_dir: Optional[str] = None) -> None:
    p = _history_path(profile, base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def record_change(profile: str, key: str, old_value: Optional[str], new_value: Optional[str],
                  action: str = "set", base_dir: Optional[str] = None) -> None:
    """Append a change entry for a key."""
    data = _read_history(profile, base_dir)
    entries = data.get(key, [])
    entries.append({
        "action": action,
        "old": old_value,
        "new": new_value,
        "timestamp": time.time(),
    })
    data[key] = entries
    _write_history(profile, data, base_dir)


def get_key_history(profile: str, key: str, base_dir: Optional[str] = None) -> list:
    """Return history entries for a specific key."""
    data = _read_history(profile, base_dir)
    return data.get(key, [])


def clear_key_history(profile: str, key: str, base_dir: Optional[str] = None) -> bool:
    """Remove all history for a key. Returns True if key existed."""
    data = _read_history(profile, base_dir)
    if key not in data:
        return False
    del data[key]
    _write_history(profile, data, base_dir)
    return True


def all_keys_with_history(profile: str, base_dir: Optional[str] = None) -> list:
    """Return list of keys that have recorded history."""
    return list(_read_history(profile, base_dir).keys())
