"""Quota management: limit the number of keys per profile."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.profile import get_vault_dir

_DEFAULT_LIMIT = 100


def _quota_path(base_dir: Optional[str] = None) -> Path:
    return Path(get_vault_dir(base_dir)) / "quota.json"


def _read_quotas(base_dir: Optional[str] = None) -> dict:
    p = _quota_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_quotas(data: dict, base_dir: Optional[str] = None) -> None:
    p = _quota_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_quota(profile: str, limit: int, base_dir: Optional[str] = None) -> None:
    if limit < 1:
        raise ValueError("Quota limit must be at least 1.")
    data = _read_quotas(base_dir)
    data[profile] = limit
    _write_quotas(data, base_dir)


def remove_quota(profile: str, base_dir: Optional[str] = None) -> None:
    data = _read_quotas(base_dir)
    data.pop(profile, None)
    _write_quotas(data, base_dir)


def get_quota(profile: str, base_dir: Optional[str] = None) -> int:
    data = _read_quotas(base_dir)
    return data.get(profile, _DEFAULT_LIMIT)


def list_quotas(base_dir: Optional[str] = None) -> dict:
    return _read_quotas(base_dir)


def check_quota(profile: str, current_count: int, base_dir: Optional[str] = None) -> None:
    limit = get_quota(profile, base_dir)
    if current_count >= limit:
        raise QuotaExceededError(
            f"Profile '{profile}' has reached its key limit of {limit}."
        )


class QuotaExceededError(Exception):
    pass
