"""Profile rating/scoring module for envoy-cli."""

import json
from pathlib import Path
from envoy.profile import get_vault_dir, profile_exists


class RatingError(Exception):
    pass


VALID_RANGE = (1, 5)


def _rating_path(base_dir: str) -> Path:
    return Path(get_vault_dir(base_dir)) / "ratings.json"


def _read_ratings(base_dir: str) -> dict:
    p = _rating_path(base_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _write_ratings(base_dir: str, data: dict) -> None:
    p = _rating_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_rating(profile: str, score: int, base_dir: str) -> None:
    """Set a rating (1-5) for a profile."""
    if not profile_exists(profile, base_dir):
        raise RatingError(f"Profile '{profile}' does not exist.")
    if not (VALID_RANGE[0] <= score <= VALID_RANGE[1]):
        raise RatingError(f"Rating must be between {VALID_RANGE[0]} and {VALID_RANGE[1]}.")
    data = _read_ratings(base_dir)
    data[profile] = score
    _write_ratings(base_dir, data)


def get_rating(profile: str, base_dir: str) -> int | None:
    """Get the rating for a profile, or None if unset."""
    data = _read_ratings(base_dir)
    return data.get(profile)


def remove_rating(profile: str, base_dir: str) -> bool:
    """Remove the rating for a profile. Returns True if removed."""
    data = _read_ratings(base_dir)
    if profile not in data:
        return False
    del data[profile]
    _write_ratings(base_dir, data)
    return True


def list_ratings(base_dir: str) -> dict:
    """Return all profile ratings as a dict."""
    return _read_ratings(base_dir)
