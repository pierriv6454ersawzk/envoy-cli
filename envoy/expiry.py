"""Key-level expiry: mark individual keys with an expiration datetime."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envoy.profile import get_vault_dir


def _expiry_path(base_dir: str, profile: str) -> Path:
    return Path(get_vault_dir(base_dir)) / f"{profile}.expiry.json"


def _read_expiry(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _write_expiry(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2))


def set_key_expiry(base_dir: str, profile: str, key: str, seconds: int) -> datetime:
    if seconds <= 0:
        raise ValueError("seconds must be a positive integer")
    path = _expiry_path(base_dir, profile)
    data = _read_expiry(path)
    expires_at = datetime.now(timezone.utc).timestamp() + seconds
    data[key] = expires_at
    _write_expiry(path, data)
    return datetime.fromtimestamp(expires_at, tz=timezone.utc)


def remove_key_expiry(base_dir: str, profile: str, key: str) -> bool:
    path = _expiry_path(base_dir, profile)
    data = _read_expiry(path)
    if key not in data:
        return False
    del data[key]
    _write_expiry(path, data)
    return True


def get_key_expiry(base_dir: str, profile: str, key: str) -> Optional[datetime]:
    path = _expiry_path(base_dir, profile)
    data = _read_expiry(path)
    if key not in data:
        return None
    return datetime.fromtimestamp(data[key], tz=timezone.utc)


def is_key_expired(base_dir: str, profile: str, key: str) -> bool:
    expiry = get_key_expiry(base_dir, profile, key)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def list_expired_keys(base_dir: str, profile: str) -> list[str]:
    path = _expiry_path(base_dir, profile)
    data = _read_expiry(path)
    now = datetime.now(timezone.utc).timestamp()
    return [k for k, ts in data.items() if now >= ts]


def list_all_expiries(base_dir: str, profile: str) -> dict[str, datetime]:
    path = _expiry_path(base_dir, profile)
    data = _read_expiry(path)
    return {k: datetime.fromtimestamp(ts, tz=timezone.utc) for k, ts in data.items()}
