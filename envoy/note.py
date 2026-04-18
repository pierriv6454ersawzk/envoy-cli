"""Per-profile and per-key notes/annotations."""
from __future__ import annotations
import json
from pathlib import Path
from envoy.profile import get_vault_dir


def _note_path(base_dir: str | None = None) -> Path:
    return Path(get_vault_dir(base_dir)) / "notes.json"


def _read_notes(base_dir: str | None = None) -> dict:
    p = _note_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_notes(data: dict, base_dir: str | None = None) -> None:
    p = _note_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_note(profile: str, note: str, key: str | None = None, base_dir: str | None = None) -> None:
    """Attach a note to a profile or a specific key within a profile."""
    data = _read_notes(base_dir)
    entry = data.setdefault(profile, {})
    field = f"__key__{key}" if key else "__profile__"
    entry[field] = note
    _write_notes(data, base_dir)


def get_note(profile: str, key: str | None = None, base_dir: str | None = None) -> str | None:
    data = _read_notes(base_dir)
    entry = data.get(profile, {})
    field = f"__key__{key}" if key else "__profile__"
    return entry.get(field)


def remove_note(profile: str, key: str | None = None, base_dir: str | None = None) -> bool:
    data = _read_notes(base_dir)
    entry = data.get(profile, {})
    field = f"__key__{key}" if key else "__profile__"
    if field not in entry:
        return False
    del entry[field]
    if not entry:
        del data[profile]
    _write_notes(data, base_dir)
    return True


def list_notes(profile: str, base_dir: str | None = None) -> dict[str, str]:
    """Return all notes for a profile keyed by field name."""
    data = _read_notes(base_dir)
    return dict(data.get(profile, {}))
