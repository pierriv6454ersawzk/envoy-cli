"""Cascade: resolve env vars by merging a chain of profiles (base -> ... -> override)."""
from __future__ import annotations
from typing import List, Dict
from envoy.profile import profile_path, profile_exists
from envoy.vault import load


class CascadeError(Exception):
    pass


def resolve_cascade(
    profiles: List[str],
    passphrase: str,
    base_dir: str | None = None,
) -> Dict[str, str]:
    """Merge profiles left-to-right; later profiles override earlier ones."""
    if not profiles:
        raise CascadeError("At least one profile must be specified.")

    merged: Dict[str, str] = {}
    for name in profiles:
        path = profile_path(name, base_dir=base_dir)
        if not profile_exists(name, base_dir=base_dir):
            raise CascadeError(f"Profile '{name}' does not exist.")
        data = load(path, passphrase)
        merged.update(data)
    return merged


def cascade_sources(
    profiles: List[str],
    passphrase: str,
    base_dir: str | None = None,
) -> Dict[str, tuple]:
    """Return a dict mapping each key to (value, winning_profile)."""
    if not profiles:
        raise CascadeError("At least one profile must be specified.")

    result: Dict[str, tuple] = {}
    for name in profiles:
        path = profile_path(name, base_dir=base_dir)
        if not profile_exists(name, base_dir=base_dir):
            raise CascadeError(f"Profile '{name}' does not exist.")
        data = load(path, passphrase)
        for k, v in data.items():
            result[k] = (v, name)
    return result
