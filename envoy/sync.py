"""Sync .env profiles between local vault and remote storage backends."""

import json
import os
from pathlib import Path
from typing import Optional

from envoy.vault import load, save
from envoy.profile import profile_path, get_vault_dir


REMOTE_INDEX_FILE = ".envoy_remote.json"


def _remote_index_path(base_dir: Optional[str] = None) -> Path:
    vault_dir = Path(get_vault_dir(base_dir))
    return vault_dir / REMOTE_INDEX_FILE


def get_remote_config(base_dir: Optional[str] = None) -> dict:
    """Load the remote backend configuration from the index file."""
    index_path = _remote_index_path(base_dir)
    if not index_path.exists():
        return {}
    with open(index_path, "r") as f:
        return json.load(f)


def set_remote_config(config: dict, base_dir: Optional[str] = None) -> None:
    """Persist remote backend configuration to the index file."""
    index_path = _remote_index_path(base_dir)
    with open(index_path, "w") as f:
        json.dump(config, f, indent=2)


def push_profile(profile: str, passphrase: str, remote_path: str, base_dir: Optional[str] = None) -> None:
    """Push an encrypted vault profile to a remote file path."""
    src = profile_path(profile, base_dir)
    if not src.exists():
        raise FileNotFoundError(f"Profile '{profile}' does not exist.")

    dest = Path(remote_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    data = load(str(src), passphrase)
    save(str(dest), passphrase, data)


def pull_profile(profile: str, passphrase: str, remote_path: str, base_dir: Optional[str] = None) -> None:
    """Pull an encrypted vault profile from a remote file path."""
    src = Path(remote_path)
    if not src.exists():
        raise FileNotFoundError(f"Remote path '{remote_path}' does not exist.")

    dest = profile_path(profile, base_dir)
    data = load(str(src), passphrase)
    save(str(dest), passphrase, data)


def diff_profiles(profile: str, passphrase: str, remote_path: str, base_dir: Optional[str] = None) -> dict:
    """Return a diff dict of keys that differ between local and remote profiles."""
    local_path = profile_path(profile, base_dir)
    if not local_path.exists():
        raise FileNotFoundError(f"Local profile '{profile}' does not exist.")
    if not Path(remote_path).exists():
        raise FileNotFoundError(f"Remote path '{remote_path}' does not exist.")

    local_data = load(str(local_path), passphrase)
    remote_data = load(remote_path, passphrase)

    all_keys = set(local_data) | set(remote_data)
    diff = {}
    for key in all_keys:
        local_val = local_data.get(key)
        remote_val = remote_data.get(key)
        if local_val != remote_val:
            diff[key] = {"local": local_val, "remote": remote_val}
    return diff
