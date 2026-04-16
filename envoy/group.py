"""Group management: assign profiles to named groups for batch operations."""
from __future__ import annotations
import json
from pathlib import Path
from envoy.profile import get_vault_dir, profile_exists


def _group_index_path(base_dir: str | None = None) -> Path:
    return get_vault_dir(base_dir) / "groups.json"


def _read_index(base_dir: str | None = None) -> dict[str, list[str]]:
    p = _group_index_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_index(index: dict[str, list[str]], base_dir: str | None = None) -> None:
    p = _group_index_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(index, indent=2))


def add_to_group(group: str, profile: str, base_dir: str | None = None) -> None:
    """Add a profile to a group."""
    if not profile_exists(profile, base_dir):
        raise ValueError(f"Profile '{profile}' does not exist.")
    index = _read_index(base_dir)
    members = index.setdefault(group, [])
    if profile not in members:
        members.append(profile)
    _write_index(index, base_dir)


def remove_from_group(group: str, profile: str, base_dir: str | None = None) -> None:
    """Remove a profile from a group."""
    index = _read_index(base_dir)
    if group not in index:
        return
    index[group] = [p for p in index[group] if p != profile]
    if not index[group]:
        del index[group]
    _write_index(index, base_dir)


def list_groups(base_dir: str | None = None) -> list[str]:
    return sorted(_read_index(base_dir).keys())


def group_members(group: str, base_dir: str | None = None) -> list[str]:
    return _read_index(base_dir).get(group, [])


def delete_group(group: str, base_dir: str | None = None) -> None:
    index = _read_index(base_dir)
    index.pop(group, None)
    _write_index(index, base_dir)


def profile_groups(profile: str, base_dir: str | None = None) -> list[str]:
    """Return all groups a profile belongs to."""
    index = _read_index(base_dir)
    return sorted(g for g, members in index.items() if profile in members)
