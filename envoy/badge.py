"""Badge module: assign and query status badges for profiles."""

import json
from pathlib import Path
from envoy.profile import get_vault_dir, profile_exists

VALID_BADGES = {"stable", "experimental", "deprecated", "reviewed", "draft"}


class BadgeError(Exception):
    pass


def _badge_path(base_dir: str) -> Path:
    return Path(get_vault_dir(base_dir)) / "badges.json"


def _read_badges(base_dir: str) -> dict:
    p = _badge_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_badges(base_dir: str, data: dict) -> None:
    _badge_path(base_dir).write_text(json.dumps(data, indent=2))


def set_badge(base_dir: str, profile: str, badge: str) -> None:
    if not profile_exists(base_dir, profile):
        raise BadgeError(f"Profile '{profile}' does not exist.")
    if badge not in VALID_BADGES:
        raise BadgeError(f"Invalid badge '{badge}'. Valid: {sorted(VALID_BADGES)}")
    data = _read_badges(base_dir)
    data[profile] = badge
    _write_badges(base_dir, data)


def remove_badge(base_dir: str, profile: str) -> None:
    data = _read_badges(base_dir)
    data.pop(profile, None)
    _write_badges(base_dir, data)


def get_badge(base_dir: str, profile: str) -> str | None:
    return _read_badges(base_dir).get(profile)


def list_badges(base_dir: str) -> dict:
    return _read_badges(base_dir)


def profiles_with_badge(base_dir: str, badge: str) -> list:
    return [p for p, b in _read_badges(base_dir).items() if b == badge]
