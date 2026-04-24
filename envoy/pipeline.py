"""Pipeline: define and run ordered sequences of envoy operations against a profile."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy.profile import get_vault_dir, profile_exists


class PipelineError(Exception):
    pass


VALID_STEPS = {"copy", "merge", "lint", "validate", "snapshot", "export"}


def _pipeline_index_path(base_dir: str | None = None) -> Path:
    return Path(get_vault_dir(base_dir)) / "pipelines.json"


def _read_index(base_dir: str | None = None) -> dict[str, Any]:
    p = _pipeline_index_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_index(data: dict[str, Any], base_dir: str | None = None) -> None:
    p = _pipeline_index_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def save_pipeline(
    name: str,
    profile: str,
    steps: list[dict[str, Any]],
    base_dir: str | None = None,
) -> None:
    """Persist a named pipeline definition."""
    if not steps:
        raise PipelineError("Pipeline must contain at least one step.")
    for step in steps:
        action = step.get("action", "")
        if action not in VALID_STEPS:
            raise PipelineError(
                f"Unknown step action '{action}'. Valid: {sorted(VALID_STEPS)}"
            )
    if not profile_exists(profile, base_dir):
        raise PipelineError(f"Profile '{profile}' does not exist.")
    index = _read_index(base_dir)
    index[name] = {"profile": profile, "steps": steps}
    _write_index(index, base_dir)


def load_pipeline(
    name: str, base_dir: str | None = None
) -> dict[str, Any]:
    """Load a named pipeline definition."""
    index = _read_index(base_dir)
    if name not in index:
        raise PipelineError(f"Pipeline '{name}' not found.")
    return index[name]


def list_pipelines(base_dir: str | None = None) -> list[str]:
    """Return names of all saved pipelines."""
    return sorted(_read_index(base_dir).keys())


def delete_pipeline(name: str, base_dir: str | None = None) -> None:
    """Remove a pipeline by name."""
    index = _read_index(base_dir)
    if name not in index:
        raise PipelineError(f"Pipeline '{name}' not found.")
    del index[name]
    _write_index(index, base_dir)
