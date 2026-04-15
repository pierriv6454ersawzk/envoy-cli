"""Snapshot: save and restore point-in-time copies of a profile's env vars."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from envoy.profile import get_vault_dir
from envoy.vault import load, save


def _snapshot_dir(base_dir: Optional[str] = None) -> Path:
    d = get_vault_dir(base_dir) / "snapshots"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _snapshot_index_path(base_dir: Optional[str] = None) -> Path:
    return _snapshot_dir(base_dir) / "index.json"


def _read_index(base_dir: Optional[str] = None) -> List[dict]:
    p = _snapshot_index_path(base_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _write_index(entries: List[dict], base_dir: Optional[str] = None) -> None:
    _snapshot_index_path(base_dir).write_text(json.dumps(entries, indent=2))


def create_snapshot(
    profile: str,
    passphrase: str,
    label: Optional[str] = None,
    base_dir: Optional[str] = None,
) -> str:
    """Snapshot current state of *profile*. Returns the snapshot id."""
    env = load(profile, passphrase, base_dir=base_dir)
    snapshot_id = f"{profile}-{int(time.time() * 1000)}"
    snap_path = _snapshot_dir(base_dir) / f"{snapshot_id}.vault"
    save(env, snapshot_id, passphrase, base_dir=str(_snapshot_dir(base_dir)))

    index = _read_index(base_dir)
    index.append({
        "id": snapshot_id,
        "profile": profile,
        "label": label or "",
        "timestamp": time.time(),
        "path": str(snap_path),
    })
    _write_index(index, base_dir)
    return snapshot_id


def list_snapshots(
    profile: Optional[str] = None,
    base_dir: Optional[str] = None,
) -> List[dict]:
    """Return snapshot index entries, optionally filtered by profile."""
    index = _read_index(base_dir)
    if profile:
        index = [e for e in index if e["profile"] == profile]
    return index


def restore_snapshot(
    snapshot_id: str,
    passphrase: str,
    target_profile: Optional[str] = None,
    base_dir: Optional[str] = None,
) -> str:
    """Restore snapshot into *target_profile* (defaults to original profile)."""
    index = _read_index(base_dir)
    entry = next((e for e in index if e["id"] == snapshot_id), None)
    if entry is None:
        raise KeyError(f"Snapshot '{snapshot_id}' not found.")

    snap_dir = str(_snapshot_dir(base_dir))
    env = load(snapshot_id, passphrase, base_dir=snap_dir)
    dest = target_profile or entry["profile"]
    save(env, dest, passphrase, base_dir=base_dir)
    return dest


def delete_snapshot(
    snapshot_id: str,
    base_dir: Optional[str] = None,
) -> None:
    """Remove a snapshot entry and its vault file."""
    index = _read_index(base_dir)
    entry = next((e for e in index if e["id"] == snapshot_id), None)
    if entry is None:
        raise KeyError(f"Snapshot '{snapshot_id}' not found.")
    snap_path = _snapshot_dir(base_dir) / f"{snapshot_id}.vault"
    if snap_path.exists():
        snap_path.unlink()
    _write_index([e for e in index if e["id"] != snapshot_id], base_dir)
