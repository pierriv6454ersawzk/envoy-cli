"""Profile priority management for envoy-cli."""

import json
from pathlib import Path
from envoy.profile import get_vault_dir, profile_exists


class PriorityError(Exception):
    pass


def _priority_path(base_dir: str) -> Path:
    return Path(get_vault_dir(base_dir)) / "priorities.json"


def _read_priorities(base_dir: str) -> dict:
    p = _priority_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_priorities(base_dir: str, data: dict) -> None:
    p = _priority_path(base_dir)
    p.write_text(json.dumps(data, indent=2))


def set_priority(base_dir: str, profile: str, priority: int) -> None:
    """Assign a numeric priority to a profile (higher = more important)."""
    if not profile_exists(base_dir, profile):
        raise PriorityError(f"Profile '{profile}' does not exist.")
    if priority < 0:
        raise PriorityError("Priority must be a non-negative integer.")
    data = _read_priorities(base_dir)
    data[profile] = priority
    _write_priorities(base_dir, data)


def remove_priority(base_dir: str, profile: str) -> None:
    """Remove priority setting for a profile."""
    data = _read_priorities(base_dir)
    data.pop(profile, None)
    _write_priorities(base_dir, data)


def get_priority(base_dir: str, profile: str) -> int:
    """Return the priority for a profile, defaulting to 0."""
    return _read_priorities(base_dir).get(profile, 0)


def list_priorities(base_dir: str) -> list:
    """Return profiles sorted by priority descending."""
    data = _read_priorities(base_dir)
    return sorted(data.items(), key=lambda x: x[1], reverse=True)
