"""Reminders: schedule a reminder message for a profile key."""
from __future__ import annotations
import json
import time
from pathlib import Path
from envoy.profile import get_vault_dir, profile_exists


class ReminderError(Exception):
    pass


def _remind_path(base_dir: str) -> Path:
    return Path(get_vault_dir(base_dir)) / "reminders.json"


def _read_reminders(base_dir: str) -> dict:
    p = _remind_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_reminders(base_dir: str, data: dict) -> None:
    _remind_path(base_dir).write_text(json.dumps(data, indent=2))


def set_reminder(base_dir: str, profile: str, key: str, message: str, due: float) -> None:
    """Set a reminder for a key in a profile. due is a Unix timestamp."""
    if not profile_exists(base_dir, profile):
        raise ReminderError(f"Profile '{profile}' does not exist.")
    if due <= time.time():
        raise ReminderError("Due time must be in the future.")
    data = _read_reminders(base_dir)
    data.setdefault(profile, {})[key] = {"message": message, "due": due}
    _write_reminders(base_dir, data)


def remove_reminder(base_dir: str, profile: str, key: str) -> bool:
    data = _read_reminders(base_dir)
    removed = data.get(profile, {}).pop(key, None)
    if removed is not None:
        _write_reminders(base_dir, data)
    return removed is not None


def get_reminder(base_dir: str, profile: str, key: str) -> dict | None:
    return _read_reminders(base_dir).get(profile, {}).get(key)


def list_reminders(base_dir: str, profile: str) -> dict[str, dict]:
    return dict(_read_reminders(base_dir).get(profile, {}))


def due_reminders(base_dir: str, profile: str) -> dict[str, dict]:
    """Return reminders whose due time has passed."""
    now = time.time()
    return {k: v for k, v in list_reminders(base_dir, profile).items() if v["due"] <= now}
