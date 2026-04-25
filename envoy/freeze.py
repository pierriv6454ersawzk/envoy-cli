"""freeze.py – mark a profile as frozen (read-only) to prevent accidental writes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from envoy.profile import get_vault_dir, profile_exists


class FreezeError(Exception):
    """Raised when a freeze/unfreeze operation cannot be completed."""


def _freeze_path(base_dir: str | None = None) -> Path:
    return Path(get_vault_dir(base_dir)) / ".freeze_index.json"


def _read_index(base_dir: str | None = None) -> Dict[str, bool]:
    path = _freeze_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _write_index(index: Dict[str, bool], base_dir: str | None = None) -> None:
    path = _freeze_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2))


def freeze_profile(profile: str, base_dir: str | None = None) -> None:
    """Mark *profile* as frozen."""
    if not profile_exists(profile, base_dir):
        raise FreezeError(f"Profile '{profile}' does not exist.")
    index = _read_index(base_dir)
    index[profile] = True
    _write_index(index, base_dir)


def unfreeze_profile(profile: str, base_dir: str | None = None) -> None:
    """Remove the frozen mark from *profile*."""
    index = _read_index(base_dir)
    index.pop(profile, None)
    _write_index(index, base_dir)


def is_frozen(profile: str, base_dir: str | None = None) -> bool:
    """Return True if *profile* is currently frozen."""
    return _read_index(base_dir).get(profile, False)


def list_frozen(base_dir: str | None = None) -> list[str]:
    """Return a sorted list of all frozen profile names."""
    return sorted(k for k, v in _read_index(base_dir).items() if v)


def assert_not_frozen(profile: str, base_dir: str | None = None) -> None:
    """Raise FreezeError if *profile* is frozen."""
    if is_frozen(profile, base_dir):
        raise FreezeError(
            f"Profile '{profile}' is frozen and cannot be modified. "
            "Use 'envoy freeze unfreeze' to unlock it."
        )
