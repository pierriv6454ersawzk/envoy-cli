"""Hook system for envoy-cli: register and run shell commands on vault events."""

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

HOOK_EVENTS = ("pre-set", "post-set", "pre-load", "post-load", "post-rotate")


def _hook_index_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envoy" / "hooks.json"


def _read_hooks(base_dir: str) -> dict:
    path = _hook_index_path(base_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _write_hooks(base_dir: str, data: dict) -> None:
    path = _hook_index_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_hook(base_dir: str, event: str, command: str) -> None:
    """Register a shell command to run on the given event."""
    if event not in HOOK_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid events: {HOOK_EVENTS}")
    hooks = _read_hooks(base_dir)
    hooks.setdefault(event, [])
    if command not in hooks[event]:
        hooks[event].append(command)
    _write_hooks(base_dir, hooks)


def remove_hook(base_dir: str, event: str, command: str) -> bool:
    """Remove a registered hook. Returns True if it was found and removed."""
    hooks = _read_hooks(base_dir)
    cmds = hooks.get(event, [])
    if command not in cmds:
        return False
    cmds.remove(command)
    hooks[event] = cmds
    _write_hooks(base_dir, hooks)
    return True


def list_hooks(base_dir: str, event: Optional[str] = None) -> dict:
    """Return all hooks, optionally filtered by event."""
    hooks = _read_hooks(base_dir)
    if event is not None:
        return {event: hooks.get(event, [])}
    return hooks


def run_hooks(base_dir: str, event: str, env: Optional[dict] = None) -> list:
    """Run all commands registered for the given event. Returns list of return codes."""
    hooks = _read_hooks(base_dir)
    commands = hooks.get(event, [])
    results = []
    merged_env = {**os.environ, **(env or {})}
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, env=merged_env)
        results.append(result.returncode)
    return results
