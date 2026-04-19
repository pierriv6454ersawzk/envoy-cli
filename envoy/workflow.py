"""Workflow: named sequences of CLI operations applied to a profile."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy.profile import get_vault_dir, profile_exists


class WorkflowError(Exception):
    pass


VALID_STEPS = {"set", "delete", "copy", "rotate", "export"}


def _workflow_index_path(base_dir: str | None = None) -> Path:
    return Path(get_vault_dir(base_dir)) / ".workflows.json"


def _read_index(base_dir: str | None = None) -> dict[str, Any]:
    path = _workflow_index_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _write_index(data: dict[str, Any], base_dir: str | None = None) -> None:
    path = _workflow_index_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def save_workflow(name: str, steps: list[dict], base_dir: str | None = None) -> None:
    """Persist a named workflow (list of step dicts)."""
    if not name or not name.isidentifier():
        raise WorkflowError(f"Invalid workflow name: {name!r}")
    for step in steps:
        action = step.get("action", "")
        if action not in VALID_STEPS:
            raise WorkflowError(f"Unknown step action: {action!r}")
    index = _read_index(base_dir)
    index[name] = steps
    _write_index(index, base_dir)


def load_workflow(name: str, base_dir: str | None = None) -> list[dict]:
    """Return steps for a named workflow, raising WorkflowError if missing."""
    index = _read_index(base_dir)
    if name not in index:
        raise WorkflowError(f"Workflow not found: {name!r}")
    return index[name]


def delete_workflow(name: str, base_dir: str | None = None) -> None:
    index = _read_index(base_dir)
    if name not in index:
        raise WorkflowError(f"Workflow not found: {name!r}")
    del index[name]
    _write_index(index, base_dir)


def list_workflows(base_dir: str | None = None) -> list[str]:
    return sorted(_read_index(base_dir).keys())
