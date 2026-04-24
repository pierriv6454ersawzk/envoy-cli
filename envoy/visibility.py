"""Profile visibility control — mark profiles as public, private, or internal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envoy.profile import get_vault_dir, profile_exists

VISIBILITY_LEVELS = ("public", "private", "internal")


class VisibilityError(Exception):
    pass


def _visibility_path(base_dir: Optional[str] = None) -> Path:
    return Path(get_vault_dir(base_dir)) / ".visibility.json"


def _read_index(base_dir: Optional[str] = None) -> Dict[str, str]:
    path = _visibility_path(base_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _write_index(index: Dict[str, str], base_dir: Optional[str] = None) -> None:
    path = _visibility_path(base_dir)
    with path.open("w") as fh:
        json.dump(index, fh, indent=2)


def set_visibility(profile: str, level: str, base_dir: Optional[str] = None) -> None:
    """Set the visibility level for *profile*."""
    if level not in VISIBILITY_LEVELS:
        raise VisibilityError(
            f"Invalid visibility level {level!r}. Choose from: {', '.join(VISIBILITY_LEVELS)}"
        )
    if not profile_exists(profile, base_dir):
        raise VisibilityError(f"Profile {profile!r} does not exist.")
    index = _read_index(base_dir)
    index[profile] = level
    _write_index(index, base_dir)


def get_visibility(profile: str, base_dir: Optional[str] = None) -> str:
    """Return the visibility level for *profile* (default: 'private')."""
    index = _read_index(base_dir)
    return index.get(profile, "private")


def remove_visibility(profile: str, base_dir: Optional[str] = None) -> None:
    """Remove an explicit visibility setting, reverting to default."""
    index = _read_index(base_dir)
    index.pop(profile, None)
    _write_index(index, base_dir)


def list_visibility(base_dir: Optional[str] = None) -> Dict[str, str]:
    """Return all explicitly-set visibility entries."""
    return dict(_read_index(base_dir))


def profiles_with_level(level: str, base_dir: Optional[str] = None) -> list[str]:
    """Return all profiles that have a specific visibility level."""
    if level not in VISIBILITY_LEVELS:
        raise VisibilityError(
            f"Invalid visibility level {level!r}. Choose from: {', '.join(VISIBILITY_LEVELS)}"
        )
    index = _read_index(base_dir)
    return [p for p, v in index.items() if v == level]
