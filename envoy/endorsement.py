"""Profile endorsement — mark a profile as reviewed/approved by a named reviewer."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from envoy.profile import get_vault_dir, profile_exists


class EndorsementError(Exception):
    pass


def _endorsement_path(base_dir: Optional[str] = None) -> Path:
    return Path(get_vault_dir(base_dir)) / "endorsements.json"


def _read_index(base_dir: Optional[str] = None) -> dict:
    p = _endorsement_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_index(index: dict, base_dir: Optional[str] = None) -> None:
    p = _endorsement_path(base_dir)
    p.write_text(json.dumps(index, indent=2))


def endorse_profile(
    profile: str,
    reviewer: str,
    note: str = "",
    base_dir: Optional[str] = None,
) -> dict:
    """Add an endorsement entry for *profile* by *reviewer*."""
    if not profile_exists(profile, base_dir):
        raise EndorsementError(f"Profile '{profile}' does not exist.")
    if not reviewer.strip():
        raise EndorsementError("Reviewer name must not be empty.")

    index = _read_index(base_dir)
    entry = {
        "reviewer": reviewer.strip(),
        "note": note,
        "timestamp": time.time(),
    }
    index.setdefault(profile, []).append(entry)
    _write_index(index, base_dir)
    return entry


def revoke_endorsement(
    profile: str,
    reviewer: str,
    base_dir: Optional[str] = None,
) -> bool:
    """Remove all endorsements for *profile* by *reviewer*. Returns True if any removed."""
    index = _read_index(base_dir)
    existing = index.get(profile, [])
    updated = [e for e in existing if e["reviewer"] != reviewer]
    if len(updated) == len(existing):
        return False
    index[profile] = updated
    _write_index(index, base_dir)
    return True


def list_endorsements(profile: str, base_dir: Optional[str] = None) -> list:
    """Return all endorsement entries for *profile*."""
    return _read_index(base_dir).get(profile, [])


def is_endorsed_by(profile: str, reviewer: str, base_dir: Optional[str] = None) -> bool:
    """Return True if *profile* has at least one endorsement from *reviewer*."""
    return any(e["reviewer"] == reviewer for e in list_endorsements(profile, base_dir))


def all_endorsements(base_dir: Optional[str] = None) -> dict:
    """Return the full endorsement index."""
    return _read_index(base_dir)
