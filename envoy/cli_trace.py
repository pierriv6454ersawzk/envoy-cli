"""CLI commands for envoy trace (operation tracing)."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from envoy.trace import clear_traces, get_traces, record_trace, summary


def _fmt_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def cmd_trace_show(args: Any) -> None:
    """Display stored traces, optionally filtered."""
    profile = getattr(args, "profile", None)
    operation = getattr(args, "operation", None)
    limit = getattr(args, "limit", 50)
    base_dir = getattr(args, "base_dir", None)

    traces = get_traces(
        profile=profile, operation=operation, limit=limit, base_dir=base_dir
    )
    if not traces:
        print("No traces found.")
        return
    for t in traces:
        detail = f"  [{t['detail']}]" if t.get("detail") else ""
        print(
            f"{_fmt_ts(t['ts'])}  {t['operation']:<20}  "
            f"{t['profile']:<20}  {t['duration_ms']:>8.1f} ms{detail}"
        )


def cmd_trace_summary(args: Any) -> None:
    """Print per-operation aggregate stats."""
    base_dir = getattr(args, "base_dir", None)
    stats = summary(base_dir=base_dir)
    if not stats:
        print("No trace data available.")
        return
    print(f"{'Operation':<22} {'Count':>6} {'Avg ms':>10} {'Max ms':>10}")
    print("-" * 52)
    for op, v in sorted(stats.items()):
        print(f"{op:<22} {v['count']:>6} {v['avg_ms']:>10.1f} {v['max_ms']:>10.1f}")


def cmd_trace_record(args: Any) -> None:
    """Manually record a trace entry (useful for scripting)."""
    operation = args.operation
    profile = args.profile
    duration_ms = getattr(args, "duration_ms", 0.0)
    detail = getattr(args, "detail", None)
    base_dir = getattr(args, "base_dir", None)

    record_trace(
        operation, profile, duration_ms, detail=detail, base_dir=base_dir
    )
    print(f"Trace recorded: {operation} on '{profile}' ({duration_ms} ms)")


def cmd_trace_clear(args: Any) -> None:
    """Clear all trace history."""
    base_dir = getattr(args, "base_dir", None)
    clear_traces(base_dir=base_dir)
    print("Trace history cleared.")


def register_trace_commands(subparsers: Any) -> None:
    p_show = subparsers.add_parser("trace-show", help="Show operation traces")
    p_show.add_argument("--profile", default=None)
    p_show.add_argument("--operation", default=None)
    p_show.add_argument("--limit", type=int, default=50)
    p_show.set_defaults(func=cmd_trace_show)

    p_sum = subparsers.add_parser("trace-summary", help="Summarise trace stats")
    p_sum.set_defaults(func=cmd_trace_summary)

    p_rec = subparsers.add_parser("trace-record", help="Record a trace entry")
    p_rec.add_argument("operation")
    p_rec.add_argument("profile")
    p_rec.add_argument("--duration-ms", type=float, default=0.0, dest="duration_ms")
    p_rec.add_argument("--detail", default=None)
    p_rec.set_defaults(func=cmd_trace_record)

    p_clr = subparsers.add_parser("trace-clear", help="Clear all traces")
    p_clr.set_defaults(func=cmd_trace_clear)
