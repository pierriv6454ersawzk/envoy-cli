"""Profile lifecycle management: mark profiles as active, inactive, or archived."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.profile import get_vault_dir, profile_exists

VALID_STATES = {"active", "inactive", "archived"}


class LifecycleError(Exception):
    pass


def _lifecycle_path(base_dir: Optional[str] = None) -> Path:
    return Path(get_vault_dir(base_dir)) / ".lifecycle.json"


def _read_index(base_dir: Optional[str] = None) -> Dict[str, str]:
    path = _lifecycle_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _write_index(index: Dict[str, str], base_dir: Optional[str] = None) -> None:
    path = _lifecycle_path(base_dir)
    path.write_text(json.dumps(index, indent=2))


def set_state(profile: str, state: str, base_dir: Optional[str] = None) -> None:
    """Set the lifecycle state of a profile."""
    if state not in VALID_STATES:
        raise LifecycleError(f"Invalid state '{state}'. Must be one of: {sorted(VALID_STATES)}")
    if not profile_exists(profile, base_dir):
        raise LifecycleError(f"Profile '{profile}' does not exist.")
    index = _read_index(base_dir)
    index[profile] = state
    _write_index(index, base_dir)


def get_state(profile: str, base_dir: Optional[str] = None) -> str:
    """Return the lifecycle state of a profile, defaulting to 'active'."""
    index = _read_index(base_dir)
    return index.get(profile, "active")


def remove_state(profile: str, base_dir: Optional[str] = None) -> None:
    """Remove explicit lifecycle state for a profile (reverts to default 'active')."""
    index = _read_index(base_dir)
    index.pop(profile, None)
    _write_index(index, base_dir)


def list_by_state(state: str, base_dir: Optional[str] = None) -> List[str]:
    """Return all profiles in the given lifecycle state."""
    if state not in VALID_STATES:
        raise LifecycleError(f"Invalid state '{state}'. Must be one of: {sorted(VALID_STATES)}")
    index = _read_index(base_dir)
    return sorted(profile for profile, s in index.items() if s == state)


def all_states(base_dir: Optional[str] = None) -> Dict[str, str]:
    """Return a mapping of all profiles with explicit lifecycle states."""
    return dict(_read_index(base_dir))
