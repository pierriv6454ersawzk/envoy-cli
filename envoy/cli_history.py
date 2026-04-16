"""CLI commands for viewing per-key change history."""

import argparse
from datetime import datetime

from envoy.history import get_key_history, clear_key_history, all_keys_with_history


def cmd_history_show(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "base_dir", None)
    entries = get_key_history(args.profile, args.key, base_dir=base_dir)
    if not entries:
        print(f"No history for key '{args.key}' in profile '{args.profile}'.")
        return
    print(f"History for '{args.key}' in profile '{args.profile}':")
    for e in entries:
        ts = datetime.fromtimestamp(e["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        action = e["action"].upper()
        old = e["old"] if e["old"] is not None else "(none)"
        new = e["new"] if e["new"] is not None else "(none)"
        print(f"  [{ts}] {action}: {old!r} -> {new!r}")


def cmd_history_keys(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "base_dir", None)
    keys = all_keys_with_history(args.profile, base_dir=base_dir)
    if not keys:
        print(f"No history recorded for profile '{args.profile}'.")
        return
    print(f"Keys with history in '{args.profile}':")
    for k in sorted(keys):
        print(f"  {k}")


def cmd_history_clear(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "base_dir", None)
    removed = clear_key_history(args.profile, args.key, base_dir=base_dir)
    if removed:
        print(f"Cleared history for '{args.key}' in profile '{args.profile}'.")
    else:
        print(f"No history found for '{args.key}' in profile '{args.profile}'.")


def register_history_commands(subparsers) -> None:
    p_show = subparsers.add_parser("history:show", help="Show change history for a key")
    p_show.add_argument("profile")
    p_show.add_argument("key")
    p_show.set_defaults(func=cmd_history_show)

    p_keys = subparsers.add_parser("history:keys", help="List keys with recorded history")
    p_keys.add_argument("profile")
    p_keys.set_defaults(func=cmd_history_keys)

    p_clear = subparsers.add_parser("history:clear", help="Clear history for a key")
    p_clear.add_argument("profile")
    p_clear.add_argument("key")
    p_clear.set_defaults(func=cmd_history_clear)
