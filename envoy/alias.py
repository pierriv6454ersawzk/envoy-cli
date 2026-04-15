"""Profile alias management — map short names to full profile names."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envoy.profile import get_vault_dir


def _alias_path(base_dir: Optional[str] = None) -> Path:
    return get_vault_dir(base_dir) / "aliases.json"


def _read_aliases(base_dir: Optional[str] = None) -> Dict[str, str]:
    path = _alias_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _write_aliases(aliases: Dict[str, str], base_dir: Optional[str] = None) -> None:
    path = _alias_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(aliases, indent=2))


def add_alias(alias: str, profile: str, base_dir: Optional[str] = None) -> None:
    """Map *alias* to *profile*. Overwrites any existing mapping."""
    if not alias or not profile:
        raise ValueError("alias and profile must be non-empty strings")
    aliases = _read_aliases(base_dir)
    aliases[alias] = profile
    _write_aliases(aliases, base_dir)


def remove_alias(alias: str, base_dir: Optional[str] = None) -> None:
    """Remove *alias*. Raises KeyError if it does not exist."""
    aliases = _read_aliases(base_dir)
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' not found")
    del aliases[alias]
    _write_aliases(aliases, base_dir)


def resolve_alias(alias: str, base_dir: Optional[str] = None) -> Optional[str]:
    """Return the profile name for *alias*, or None if not found."""
    return _read_aliases(base_dir).get(alias)


def list_aliases(base_dir: Optional[str] = None) -> Dict[str, str]:
    """Return all alias → profile mappings."""
    return dict(_read_aliases(base_dir))
