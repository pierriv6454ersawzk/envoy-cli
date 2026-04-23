"""envoy.trace — lightweight operation tracing for profiling CLI actions."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from envoy.profile import get_vault_dir


def _trace_path(base_dir: str | None = None) -> Path:
    return Path(get_vault_dir(base_dir)) / "traces.json"


def _read_traces(base_dir: str | None = None) -> list[dict[str, Any]]:
    p = _trace_path(base_dir)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _write_traces(traces: list[dict[str, Any]], base_dir: str | None = None) -> None:
    p = _trace_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(traces, indent=2))


def record_trace(
    operation: str,
    profile: str,
    duration_ms: float,
    *,
    detail: str | None = None,
    base_dir: str | None = None,
) -> None:
    """Append a trace entry for a completed operation."""
    traces = _read_traces(base_dir)
    entry: dict[str, Any] = {
        "ts": time.time(),
        "operation": operation,
        "profile": profile,
        "duration_ms": round(duration_ms, 3),
    }
    if detail:
        entry["detail"] = detail
    traces.append(entry)
    _write_traces(traces, base_dir)


def get_traces(
    profile: str | None = None,
    operation: str | None = None,
    limit: int = 100,
    base_dir: str | None = None,
) -> list[dict[str, Any]]:
    """Return traces, optionally filtered by profile and/or operation."""
    traces = _read_traces(base_dir)
    if profile:
        traces = [t for t in traces if t.get("profile") == profile]
    if operation:
        traces = [t for t in traces if t.get("operation") == operation]
    return traces[-limit:]


def clear_traces(base_dir: str | None = None) -> None:
    """Remove all stored traces."""
    _write_traces([], base_dir)


def summary(
    base_dir: str | None = None,
) -> dict[str, dict[str, float]]:
    """Return per-operation stats: count, avg_ms, max_ms."""
    traces = _read_traces(base_dir)
    stats: dict[str, dict[str, Any]] = {}
    for t in traces:
        op = t.get("operation", "unknown")
        ms = t.get("duration_ms", 0.0)
        if op not in stats:
            stats[op] = {"count": 0, "total_ms": 0.0, "max_ms": 0.0}
        stats[op]["count"] += 1
        stats[op]["total_ms"] += ms
        if ms > stats[op]["max_ms"]:
            stats[op]["max_ms"] = ms
    return {
        op: {
            "count": v["count"],
            "avg_ms": round(v["total_ms"] / v["count"], 3),
            "max_ms": round(v["max_ms"], 3),
        }
        for op, v in stats.items()
    }
