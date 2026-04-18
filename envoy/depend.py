"""Profile dependency tracking for envoy-cli."""

import json
from pathlib import Path
from envoy.profile import get_vault_dir, profile_exists


class DependencyError(Exception):
    pass


def _dep_index_path(base_dir: str) -> Path:
    return Path(get_vault_dir(base_dir)) / ".dependencies.json"


def _read_index(base_dir: str) -> dict:
    p = _dep_index_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_index(base_dir: str, data: dict) -> None:
    _dep_index_path(base_dir).write_text(json.dumps(data, indent=2))


def add_dependency(base_dir: str, profile: str, depends_on: str) -> None:
    """Record that `profile` depends on `depends_on`."""
    if not profile_exists(base_dir, profile):
        raise DependencyError(f"Profile not found: {profile}")
    if not profile_exists(base_dir, depends_on):
        raise DependencyError(f"Profile not found: {depends_on}")
    if profile == depends_on:
        raise DependencyError("A profile cannot depend on itself.")
    index = _read_index(base_dir)
    deps = set(index.get(profile, []))
    deps.add(depends_on)
    index[profile] = sorted(deps)
    _write_index(base_dir, index)


def remove_dependency(base_dir: str, profile: str, depends_on: str) -> None:
    index = _read_index(base_dir)
    deps = set(index.get(profile, []))
    deps.discard(depends_on)
    if deps:
        index[profile] = sorted(deps)
    else:
        index.pop(profile, None)
    _write_index(base_dir, index)


def get_dependencies(base_dir: str, profile: str) -> list:
    return _read_index(base_dir).get(profile, [])


def get_dependents(base_dir: str, profile: str) -> list:
    """Return profiles that depend on the given profile."""
    return [p for p, deps in _read_index(base_dir).items() if profile in deps]


def list_all(base_dir: str) -> dict:
    return _read_index(base_dir)
