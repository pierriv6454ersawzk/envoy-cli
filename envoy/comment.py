"""Per-key inline comments stored alongside vault profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envoy.profile import get_vault_dir, profile_exists


class CommentError(Exception):
    pass


def _comment_path(base_dir: str, profile: str) -> Path:
    return Path(get_vault_dir(base_dir)) / f"{profile}.comments.json"


def _read_comments(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _write_comments(path: Path, data: Dict[str, str]) -> None:
    path.write_text(json.dumps(data, indent=2))


def set_comment(base_dir: str, profile: str, key: str, comment: str) -> None:
    if not profile_exists(base_dir, profile):
        raise CommentError(f"Profile '{profile}' does not exist.")
    if not key.strip():
        raise CommentError("Key must not be empty.")
    path = _comment_path(base_dir, profile)
    data = _read_comments(path)
    data[key] = comment
    _write_comments(path, data)


def get_comment(base_dir: str, profile: str, key: str) -> Optional[str]:
    path = _comment_path(base_dir, profile)
    return _read_comments(path).get(key)


def remove_comment(base_dir: str, profile: str, key: str) -> bool:
    path = _comment_path(base_dir, profile)
    data = _read_comments(path)
    if key not in data:
        return False
    del data[key]
    _write_comments(path, data)
    return True


def list_comments(base_dir: str, profile: str) -> Dict[str, str]:
    path = _comment_path(base_dir, profile)
    return _read_comments(path)
