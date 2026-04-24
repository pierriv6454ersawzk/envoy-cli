"""Checkpoint support: save and restore named env snapshots with metadata."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from envoy.profile import get_vault_dir
from envoy.vault import load, save


class CheckpointError(Exception):
    pass


def _checkpoint_dir(base_dir: Optional[str] = None) -> Path:
    return Path(get_vault_dir(base_dir)) / ".checkpoints"


def _index_path(base_dir: Optional[str] = None) -> Path:
    return _checkpoint_dir(base_dir) / "index.json"


def _read_index(base_dir: Optional[str] = None) -> Dict:
    path = _index_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _write_index(index: Dict, base_dir: Optional[str] = None) -> None:
    path = _index_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2))


def create_checkpoint(
    profile: str,
    passphrase: str,
    name: str,
    base_dir: Optional[str] = None,
) -> str:
    """Save a named checkpoint for a profile. Returns the checkpoint name."""
    from envoy.profile import profile_exists

    if not profile_exists(profile, base_dir):
        raise CheckpointError(f"Profile '{profile}' does not exist.")

    env = load(profile, passphrase, base_dir)
    ckpt_dir = _checkpoint_dir(base_dir) / profile
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    ckpt_file = ckpt_dir / f"{name}.json"
    ckpt_file.write_text(json.dumps(env))

    index = _read_index(base_dir)
    if profile not in index:
        index[profile] = {}
    index[profile][name] = {"created_at": time.time(), "key_count": len(env)}
    _write_index(index, base_dir)
    return name


def list_checkpoints(profile: str, base_dir: Optional[str] = None) -> List[Dict]:
    """Return all checkpoints for a profile, sorted by creation time."""
    index = _read_index(base_dir)
    entries = index.get(profile, {})
    return sorted(
        [{"name": k, **v} for k, v in entries.items()],
        key=lambda e: e["created_at"],
    )


def restore_checkpoint(
    profile: str,
    name: str,
    passphrase: str,
    base_dir: Optional[str] = None,
) -> None:
    """Restore a profile's env from a named checkpoint."""
    ckpt_file = _checkpoint_dir(base_dir) / profile / f"{name}.json"
    if not ckpt_file.exists():
        raise CheckpointError(f"Checkpoint '{name}' not found for profile '{profile}'.")
    env = json.loads(ckpt_file.read_text())
    save(profile, passphrase, env, base_dir)


def delete_checkpoint(
    profile: str,
    name: str,
    base_dir: Optional[str] = None,
) -> None:
    """Delete a named checkpoint."""
    ckpt_file = _checkpoint_dir(base_dir) / profile / f"{name}.json"
    if not ckpt_file.exists():
        raise CheckpointError(f"Checkpoint '{name}' not found for profile '{profile}'.")
    ckpt_file.unlink()
    index = _read_index(base_dir)
    if profile in index and name in index[profile]:
        del index[profile][name]
        _write_index(index, base_dir)
