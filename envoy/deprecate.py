"""Key deprecation tracking for envoy profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.profile import get_vault_dir, profile_exists


class DeprecationError(Exception):
    pass


def _deprecate_path(base_dir: Optional[str] = None) -> Path:
    return Path(get_vault_dir(base_dir)) / ".deprecations.json"


def _read_index(base_dir: Optional[str] = None) -> dict:
    path = _deprecate_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _write_index(index: dict, base_dir: Optional[str] = None) -> None:
    path = _deprecate_path(base_dir)
    path.write_text(json.dumps(index, indent=2))


def deprecate_key(
    profile: str,
    key: str,
    reason: str = "",
    replacement: Optional[str] = None,
    base_dir: Optional[str] = None,
) -> None:
    """Mark a key as deprecated in a profile."""
    if not profile_exists(profile, base_dir):
        raise DeprecationError(f"Profile '{profile}' does not exist.")
    index = _read_index(base_dir)
    index.setdefault(profile, {})[key] = {
        "reason": reason,
        "replacement": replacement,
    }
    _write_index(index, base_dir)


def undeprecate_key(profile: str, key: str, base_dir: Optional[str] = None) -> None:
    """Remove deprecation marker from a key."""
    index = _read_index(base_dir)
    if profile in index and key in index[profile]:
        del index[profile][key]
        if not index[profile]:
            del index[profile]
        _write_index(index, base_dir)


def get_deprecation(
    profile: str, key: str, base_dir: Optional[str] = None
) -> Optional[dict]:
    """Return deprecation info for a key, or None if not deprecated."""
    index = _read_index(base_dir)
    return index.get(profile, {}).get(key)


def list_deprecated_keys(
    profile: str, base_dir: Optional[str] = None
) -> dict[str, dict]:
    """Return all deprecated keys for a profile."""
    index = _read_index(base_dir)
    return dict(index.get(profile, {}))


def is_deprecated(profile: str, key: str, base_dir: Optional[str] = None) -> bool:
    """Return True if the key is marked deprecated in the given profile."""
    return get_deprecation(profile, key, base_dir) is not None
