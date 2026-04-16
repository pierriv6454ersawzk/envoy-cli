"""CLI commands for quota management."""

from __future__ import annotations

import sys
from typing import Optional

from envoy.quota import set_quota, remove_quota, get_quota, list_quotas


def cmd_quota_set(args, base_dir: Optional[str] = None) -> None:
    try:
        limit = int(args.limit)
    except ValueError:
        print(f"Error: limit must be an integer.", file=sys.stderr)
        sys.exit(1)
    try:
        set_quota(args.profile, limit, base_dir=base_dir)
        print(f"Quota for '{args.profile}' set to {limit} keys.")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_quota_remove(args, base_dir: Optional[str] = None) -> None:
    remove_quota(args.profile, base_dir=base_dir)
    print(f"Quota removed for '{args.profile}'. Default limit applies.")


def cmd_quota_show(args, base_dir: Optional[str] = None) -> None:
    limit = get_quota(args.profile, base_dir=base_dir)
    print(f"Quota for '{args.profile}': {limit} keys")


def cmd_quota_list(args, base_dir: Optional[str] = None) -> None:
    quotas = list_quotas(base_dir=base_dir)
    if not quotas:
        print("No custom quotas set.")
        return
    for profile, limit in sorted(quotas.items()):
        print(f"  {profile}: {limit} keys")


def register_quota_commands(subparsers, base_dir: Optional[str] = None) -> None:
    p = subparsers.add_parser("quota", help="Manage per-profile key quotas")
    sub = p.add_subparsers(dest="quota_cmd")

    ps = sub.add_parser("set", help="Set key limit for a profile")
    ps.add_argument("profile")
    ps.add_argument("limit")
    ps.set_defaults(func=lambda a: cmd_quota_set(a, base_dir=base_dir))

    pr = sub.add_parser("remove", help="Remove custom quota for a profile")
    pr.add_argument("profile")
    pr.set_defaults(func=lambda a: cmd_quota_remove(a, base_dir=base_dir))

    psh = sub.add_parser("show", help="Show quota for a profile")
    psh.add_argument("profile")
    psh.set_defaults(func=lambda a: cmd_quota_show(a, base_dir=base_dir))

    pl = sub.add_parser("list", help="List all custom quotas")
    pl.set_defaults(func=lambda a: cmd_quota_list(a, base_dir=base_dir))
