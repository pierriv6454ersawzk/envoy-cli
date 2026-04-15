"""Pin management: lock a profile to a specific snapshot for reproducibility."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.profile import get_vault_dir


def _pin_path(base_dir: Optional[str] = None) -> Path:
    return get_vault_dir(base_dir) / "pins.json"


def _read_pins(base_dir: Optional[str] = None) -> dict:
    p = _pin_path(base_dir)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _write_pins(pins: dict, base_dir: Optional[str] = None) -> None:
    p = _pin_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(pins, f, indent=2)


def pin_profile(profile: str, snapshot_id: str, base_dir: Optional[str] = None) -> None:
    """Pin a profile to a specific snapshot ID."""
    pins = _read_pins(base_dir)
    pins[profile] = snapshot_id
    _write_pins(pins, base_dir)


def unpin_profile(profile: str, base_dir: Optional[str] = None) -> None:
    """Remove the pin for a profile. Raises KeyError if not pinned."""
    pins = _read_pins(base_dir)
    if profile not in pins:
        raise KeyError(f"Profile '{profile}' is not pinned.")
    del pins[profile]
    _write_pins(pins, base_dir)


def get_pin(profile: str, base_dir: Optional[str] = None) -> Optional[str]:
    """Return the snapshot ID pinned to a profile, or None."""
    return _read_pins(base_dir).get(profile)


def list_pins(base_dir: Optional[str] = None) -> dict:
    """Return all profile -> snapshot_id mappings."""
    return dict(_read_pins(base_dir))
