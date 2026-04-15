"""Audit log for tracking vault access and modifications."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_FILENAME = "audit.log"


def _audit_path(base_dir: Optional[str] = None) -> Path:
    """Return the path to the audit log file."""
    from envoy.profile import get_vault_dir
    vault_dir = Path(base_dir) if base_dir else get_vault_dir()
    return vault_dir / AUDIT_FILENAME


def record(action: str, profile: str, key: Optional[str] = None,
           base_dir: Optional[str] = None) -> None:
    """Append an audit entry for the given action."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "profile": profile,
    }
    if key is not None:
        entry["key"] = key

    path = _audit_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read_log(base_dir: Optional[str] = None) -> list[dict]:
    """Return all audit entries as a list of dicts."""
    path = _audit_path(base_dir)
    if not path.exists():
        return []
    entries = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def clear_log(base_dir: Optional[str] = None) -> None:
    """Remove the audit log file if it exists."""
    path = _audit_path(base_dir)
    if path.exists():
        path.unlink()
