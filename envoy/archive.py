"""Archive and restore entire vault directories as compressed bundles."""

import json
import tarfile
import io
import os
import time
from pathlib import Path
from envoy.profile import get_vault_dir, list_profiles


def _archive_index_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envoy_archives" / "index.json"


def _read_index(base_dir: str) -> list:
    p = _archive_index_path(base_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _write_index(base_dir: str, index: list) -> None:
    p = _archive_index_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(index, indent=2))


def create_archive(base_dir: str, label: str = "") -> Path:
    """Bundle all profile vault files into a .tar.gz archive."""
    vault_dir = Path(get_vault_dir(base_dir))
    archive_dir = Path(base_dir) / ".envoy_archives"
    archive_dir.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    archive_name = f"archive_{timestamp}.tar.gz"
    archive_path = archive_dir / archive_name

    with tarfile.open(archive_path, "w:gz") as tar:
        if vault_dir.exists():
            tar.add(vault_dir, arcname="vault")

    index = _read_index(base_dir)
    index.append({"file": archive_name, "timestamp": timestamp, "label": label})
    _write_index(base_dir, index)

    return archive_path


def list_archives(base_dir: str) -> list:
    """Return metadata for all archives."""
    return _read_index(base_dir)


def restore_archive(base_dir: str, archive_name: str) -> None:
    """Extract an archive, overwriting current vault files."""
    archive_path = Path(base_dir) / ".envoy_archives" / archive_name
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_name}")

    vault_dir = Path(get_vault_dir(base_dir))
    with tarfile.open(archive_path, "r:gz") as tar:
        for member in tar.getmembers():
            member.name = member.name.replace("vault/", "", 1)
            tar.extract(member, path=vault_dir)


def delete_archive(base_dir: str, archive_name: str) -> bool:
    """Delete an archive file and remove from index."""
    archive_path = Path(base_dir) / ".envoy_archives" / archive_name
    if not archive_path.exists():
        return False
    archive_path.unlink()
    index = [e for e in _read_index(base_dir) if e["file"] != archive_name]
    _write_index(base_dir, index)
    return True
