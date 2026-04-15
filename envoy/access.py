"""Access control: restrict which profiles a passphrase may unlock."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.profile import get_vault_dir


def _acl_path(base_dir: Optional[str] = None) -> Path:
    return get_vault_dir(base_dir) / "access_control.json"


def _read_acl(base_dir: Optional[str] = None) -> Dict[str, List[str]]:
    path = _acl_path(base_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _write_acl(acl: Dict[str, List[str]], base_dir: Optional[str] = None) -> None:
    path = _acl_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(acl, fh, indent=2)


def grant_access(profile: str, label: str, base_dir: Optional[str] = None) -> None:
    """Grant *label* access to *profile*."""
    acl = _read_acl(base_dir)
    labels = acl.setdefault(profile, [])
    if label not in labels:
        labels.append(label)
    _write_acl(acl, base_dir)


def revoke_access(profile: str, label: str, base_dir: Optional[str] = None) -> None:
    """Revoke *label* access from *profile*. Silently ignores missing entries."""
    acl = _read_acl(base_dir)
    labels = acl.get(profile, [])
    if label in labels:
        labels.remove(label)
    if not labels:
        acl.pop(profile, None)
    _write_acl(acl, base_dir)


def list_access(profile: str, base_dir: Optional[str] = None) -> List[str]:
    """Return all labels that have access to *profile*."""
    return _read_acl(base_dir).get(profile, [])


def has_access(profile: str, label: str, base_dir: Optional[str] = None) -> bool:
    """Return True if *label* has access to *profile*."""
    return label in list_access(profile, base_dir)


def all_grants(base_dir: Optional[str] = None) -> Dict[str, List[str]]:
    """Return the full ACL mapping."""
    return _read_acl(base_dir)
