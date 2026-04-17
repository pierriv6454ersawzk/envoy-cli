"""Bookmark frequently used key-value lookups for quick access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy.profile import get_vault_dir


def _bookmark_path(base_dir: Optional[str] = None) -> Path:
    return Path(get_vault_dir(base_dir)) / "bookmarks.json"


def _read_bookmarks(base_dir: Optional[str] = None) -> dict:
    p = _bookmark_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_bookmarks(data: dict, base_dir: Optional[str] = None) -> None:
    p = _bookmark_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def add_bookmark(name: str, profile: str, key: str, base_dir: Optional[str] = None) -> None:
    """Bookmark a key in a profile under a short name."""
    if not name.strip():
        raise ValueError("Bookmark name must not be empty.")
    data = _read_bookmarks(base_dir)
    data[name] = {"profile": profile, "key": key}
    _write_bookmarks(data, base_dir)


def remove_bookmark(name: str, base_dir: Optional[str] = None) -> None:
    """Remove a bookmark by name."""
    data = _read_bookmarks(base_dir)
    if name not in data:
        raise KeyError(f"Bookmark '{name}' not found.")
    del data[name]
    _write_bookmarks(data, base_dir)


def get_bookmark(name: str, base_dir: Optional[str] = None) -> Optional[dict]:
    """Return bookmark entry or None."""
    return _read_bookmarks(base_dir).get(name)


def list_bookmarks(base_dir: Optional[str] = None) -> dict:
    """Return all bookmarks."""
    return _read_bookmarks(base_dir)
