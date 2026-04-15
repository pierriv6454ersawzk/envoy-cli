"""Tag management for env profiles — attach, remove, and filter profiles by tag."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envoy.profile import get_vault_dir


def _tag_index_path(base_dir: str | None = None) -> Path:
    return get_vault_dir(base_dir) / "tags.json"


def _read_index(base_dir: str | None = None) -> Dict[str, List[str]]:
    """Return mapping of profile -> [tags]."""
    p = _tag_index_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_index(index: Dict[str, List[str]], base_dir: str | None = None) -> None:
    p = _tag_index_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(index, indent=2))


def add_tag(profile: str, tag: str, base_dir: str | None = None) -> None:
    """Add *tag* to *profile*. No-op if already present."""
    index = _read_index(base_dir)
    tags = index.setdefault(profile, [])
    if tag not in tags:
        tags.append(tag)
    _write_index(index, base_dir)


def remove_tag(profile: str, tag: str, base_dir: str | None = None) -> None:
    """Remove *tag* from *profile*. No-op if not present."""
    index = _read_index(base_dir)
    if profile in index:
        index[profile] = [t for t in index[profile] if t != tag]
        if not index[profile]:
            del index[profile]
    _write_index(index, base_dir)


def list_tags(profile: str, base_dir: str | None = None) -> List[str]:
    """Return all tags attached to *profile*."""
    return _read_index(base_dir).get(profile, [])


def profiles_with_tag(tag: str, base_dir: str | None = None) -> List[str]:
    """Return all profiles that carry *tag*."""
    index = _read_index(base_dir)
    return [profile for profile, tags in index.items() if tag in tags]


def all_tags(base_dir: str | None = None) -> Dict[str, List[str]]:
    """Return the full profile -> tags mapping."""
    return _read_index(base_dir)
