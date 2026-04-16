"""CLI commands for managing per-key expiry."""

from __future__ import annotations

import sys
from datetime import timezone

from envoy import expiry as exp


def cmd_expiry_set(args) -> None:
    try:
        seconds = int(args.seconds)
    except ValueError:
        print(f"Error: seconds must be an integer, got '{args.seconds}'", file=sys.stderr)
        sys.exit(1)
    try:
        expires_at = exp.set_key_expiry(args.base_dir, args.profile, args.key, seconds)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Key '{args.key}' in profile '{args.profile}' expires at {expires_at.isoformat()}")


def cmd_expiry_remove(args) -> None:
    removed = exp.remove_key_expiry(args.base_dir, args.profile, args.key)
    if not removed:
        print(f"No expiry set for key '{args.key}' in profile '{args.profile}'.", file=sys.stderr)
        sys.exit(1)
    print(f"Expiry removed for key '{args.key}' in profile '{args.profile}'.")


def cmd_expiry_show(args) -> None:
    dt = exp.get_key_expiry(args.base_dir, args.profile, args.key)
    if dt is None:
        print(f"No expiry set for key '{args.key}'.")
        return
    expired = exp.is_key_expired(args.base_dir, args.profile, args.key)
    status = "EXPIRED" if expired else "active"
    print(f"{args.key}: {dt.isoformat()} [{status}]")


def cmd_expiry_list(args) -> None:
    all_exp = exp.list_all_expiries(args.base_dir, args.profile)
    if not all_exp:
        print(f"No expiries set for profile '{args.profile}'.")
        return
    now_ts = __import__('datetime').datetime.now(timezone.utc)
    for key, dt in sorted(all_exp.items()):
        status = "EXPIRED" if now_ts >= dt else "active"
        print(f"  {key}: {dt.isoformat()} [{status}]")


def register_expiry_commands(subparsers, common) -> None:
    p = subparsers.add_parser("expiry-set", parents=[common], help="Set expiry on a key")
    p.add_argument("profile")
    p.add_argument("key")
    p.add_argument("seconds")
    p.set_defaults(func=cmd_expiry_set)

    p = subparsers.add_parser("expiry-remove", parents=[common], help="Remove expiry from a key")
    p.add_argument("profile")
    p.add_argument("key")
    p.set_defaults(func=cmd_expiry_remove)

    p = subparsers.add_parser("expiry-show", parents=[common], help="Show expiry for a key")
    p.add_argument("profile")
    p.add_argument("key")
    p.set_defaults(func=cmd_expiry_show)

    p = subparsers.add_parser("expiry-list", parents=[common], help="List all key expiries for a profile")
    p.add_argument("profile")
    p.set_defaults(func=cmd_expiry_list)
