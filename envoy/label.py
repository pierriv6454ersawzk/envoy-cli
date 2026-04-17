"""Label management for env profiles."""
from __future__ import annotations
import json
from pathlib import Path
from envoy.profile import get_vault_dir, profile_exists


class LabelError(Exception):
    pass


def _label_index_path(base_dir: str | None = None) -> Path:
    return Path(get_vault_dir(base_dir)) / "labels.json"


def _read_index(base_dir: str | None = None) -> dict[str, list[str]]:
    p = _label_index_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_index(index: dict[str, list[str]], base_dir: str | None = None) -> None:
    p = _label_index_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(index, indent=2))


def add_label(profile: str, label: str, base_dir: str | None = None) -> None:
    if not profile_exists(profile, base_dir):
        raise LabelError(f"Profile '{profile}' does not exist.")
    label = label.strip()
    if not label:
        raise LabelError("Label must not be empty.")
    index = _read_index(base_dir)
    labels = index.get(profile, [])
    if label not in labels:
        labels.append(label)
    index[profile] = labels
    _write_index(index, base_dir)


def remove_label(profile: str, label: str, base_dir: str | None = None) -> None:
    index = _read_index(base_dir)
    labels = index.get(profile, [])
    if label not in labels:
        raise LabelError(f"Label '{label}' not found on profile '{profile}'.")
    labels.remove(label)
    index[profile] = labels
    _write_index(index, base_dir)


def list_labels(profile: str, base_dir: str | None = None) -> list[str]:
    return _read_index(base_dir).get(profile, [])


def find_by_label(label: str, base_dir: str | None = None) -> list[str]:
    return [p for p, labels in _read_index(base_dir).items() if label in labels]


def all_labels(base_dir: str | None = None) -> dict[str, list[str]]:
    return _read_index(base_dir)
