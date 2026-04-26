"""Trust management for envoy profiles.

Allows marking profiles as trusted or untrusted, with an optional reason
and timestamp. Trusted profiles can be used to signal that a profile has
been reviewed and approved for use in a given context.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from envoy.profile import get_vault_dir, profile_exists


class TrustError(Exception):
    pass


def _trust_path(base_dir: Optional[str] = None) -> Path:
    return Path(get_vault_dir(base_dir)) / "trust_index.json"


def _read_index(base_dir: Optional[str] = None) -> dict:
    p = _trust_path(base_dir)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _write_index(index: dict, base_dir: Optional[str] = None) -> None:
    p = _trust_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(index, f, indent=2)


def trust_profile(
    profile: str,
    reason: str = "",
    base_dir: Optional[str] = None,
) -> dict:
    """Mark a profile as trusted."""
    if not profile_exists(profile, base_dir):
        raise TrustError(f"Profile '{profile}' does not exist.")
    index = _read_index(base_dir)
    entry = {
        "trusted": True,
        "reason": reason,
        "timestamp": time.time(),
    }
    index[profile] = entry
    _write_index(index, base_dir)
    return entry


def revoke_trust(
    profile: str,
    base_dir: Optional[str] = None,
) -> None:
    """Remove trust designation from a profile."""
    index = _read_index(base_dir)
    if profile not in index:
        raise TrustError(f"Profile '{profile}' has no trust record.")
    del index[profile]
    _write_index(index, base_dir)


def is_trusted(profile: str, base_dir: Optional[str] = None) -> bool:
    """Return True if the profile is currently trusted."""
    index = _read_index(base_dir)
    return index.get(profile, {}).get("trusted", False)


def get_trust_record(
    profile: str, base_dir: Optional[str] = None
) -> Optional[dict]:
    """Return the trust record for a profile, or None if not trusted."""
    return _read_index(base_dir).get(profile)


def list_trusted(base_dir: Optional[str] = None) -> list[str]:
    """Return a list of all trusted profile names."""
    index = _read_index(base_dir)
    return [p for p, v in index.items() if v.get("trusted")]
