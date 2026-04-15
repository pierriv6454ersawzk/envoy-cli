"""TTL (time-to-live) support for profile keys — automatically expire keys after a set duration."""

import json
import time
from pathlib import Path
from typing import Optional

from envoy.profile import get_vault_dir


def _ttl_path(profile: str, base_dir: Optional[str] = None) -> Path:
    return get_vault_dir(base_dir) / f"{profile}.ttl.json"


def _read_ttl_index(profile: str, base_dir: Optional[str] = None) -> dict:
    path = _ttl_path(profile, base_dir)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _write_ttl_index(profile: str, index: dict, base_dir: Optional[str] = None) -> None:
    path = _ttl_path(profile, base_dir)
    with path.open("w") as f:
        json.dump(index, f, indent=2)


def set_ttl(profile: str, key: str, seconds: int, base_dir: Optional[str] = None) -> None:
    """Set a TTL (in seconds from now) for a key in a profile."""
    if seconds <= 0:
        raise ValueError("TTL must be a positive number of seconds.")
    index = _read_ttl_index(profile, base_dir)
    index[key] = time.time() + seconds
    _write_ttl_index(profile, index, base_dir)


def remove_ttl(profile: str, key: str, base_dir: Optional[str] = None) -> None:
    """Remove the TTL for a key, making it permanent."""
    index = _read_ttl_index(profile, base_dir)
    index.pop(key, None)
    _write_ttl_index(profile, index, base_dir)


def get_ttl(profile: str, key: str, base_dir: Optional[str] = None) -> Optional[float]:
    """Return the expiry timestamp for a key, or None if no TTL is set."""
    index = _read_ttl_index(profile, base_dir)
    return index.get(key)


def is_expired(profile: str, key: str, base_dir: Optional[str] = None) -> bool:
    """Return True if the key has a TTL that has already passed."""
    expiry = get_ttl(profile, key, base_dir)
    if expiry is None:
        return False
    return time.time() > expiry


def expired_keys(profile: str, base_dir: Optional[str] = None) -> list:
    """Return a list of keys whose TTL has expired."""
    index = _read_ttl_index(profile, base_dir)
    now = time.time()
    return [key for key, expiry in index.items() if now > expiry]


def purge_expired(profile: str, base_dir: Optional[str] = None) -> list:
    """Remove all expired TTL entries from the index and return their keys."""
    index = _read_ttl_index(profile, base_dir)
    now = time.time()
    expired = [key for key, expiry in index.items() if now > expiry]
    for key in expired:
        del index[key]
    _write_ttl_index(profile, index, base_dir)
    return expired
