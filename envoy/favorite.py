"""Favorite profiles — mark profiles as favorites for quick access."""

from __future__ import annotations

import json
from pathlib import Path

from envoy.profile import get_vault_dir, profile_exists


def _favorite_path(base_dir: str | None = None) -> Path:
    return get_vault_dir(base_dir) / "favorites.json"


def _read_favorites(base_dir: str | None = None) -> list[str]:
    path = _favorite_path(base_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _write_favorites(favorites: list[str], base_dir: str | None = None) -> None:
    path = _favorite_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(favorites, indent=2))


def add_favorite(profile: str, base_dir: str | None = None) -> None:
    """Mark a profile as a favorite."""
    if not profile_exists(profile, base_dir):
        raise ValueError(f"Profile '{profile}' does not exist.")
    favorites = _read_favorites(base_dir)
    if profile not in favorites:
        favorites.append(profile)
        _write_favorites(favorites, base_dir)


def remove_favorite(profile: str, base_dir: str | None = None) -> None:
    """Remove a profile from favorites."""
    favorites = _read_favorites(base_dir)
    if profile not in favorites:
        raise ValueError(f"Profile '{profile}' is not a favorite.")
    favorites.remove(profile)
    _write_favorites(favorites, base_dir)


def list_favorites(base_dir: str | None = None) -> list[str]:
    """Return all favorited profile names."""
    return _read_favorites(base_dir)


def is_favorite(profile: str, base_dir: str | None = None) -> bool:
    """Return True if the profile is marked as a favorite."""
    return profile in _read_favorites(base_dir)
