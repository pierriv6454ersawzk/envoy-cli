"""CLI commands for access-control management."""

from __future__ import annotations

import argparse
import sys

from envoy.access import (
    all_grants,
    grant_access,
    has_access,
    list_access,
    revoke_access,
)


def cmd_access_grant(args: argparse.Namespace) -> None:
    """Grant a label access to a profile."""
    if not args.profile or not args.label:
        print("Error: --profile and --label are required.", file=sys.stderr)
        sys.exit(1)
    grant_access(args.profile, args.label, base_dir=args.base_dir)
    print(f"Granted '{args.label}' access to profile '{args.profile}'.")


def cmd_access_revoke(args: argparse.Namespace) -> None:
    """Revoke a label's access from a profile."""
    if not args.profile or not args.label:
        print("Error: --profile and --label are required.", file=sys.stderr)
        sys.exit(1)
    revoke_access(args.profile, args.label, base_dir=args.base_dir)
    print(f"Revoked '{args.label}' access from profile '{args.profile}'.")


def cmd_access_list(args: argparse.Namespace) -> None:
    """List labels that have access to a profile."""
    if not args.profile:
        print("Error: --profile is required.", file=sys.stderr)
        sys.exit(1)
    labels = list_access(args.profile, base_dir=args.base_dir)
    if not labels:
        print(f"No access labels for profile '{args.profile}'.")
    else:
        for label in labels:
            print(label)


def cmd_access_show_all(args: argparse.Namespace) -> None:
    """Show the full access-control list."""
    grants = all_grants(base_dir=args.base_dir)
    if not grants:
        print("No access control entries found.")
        return
    for profile, labels in sorted(grants.items()):
        print(f"{profile}: {', '.join(labels)}")


def cmd_access_check(args: argparse.Namespace) -> None:
    """Check whether a label has access to a profile."""
    if not args.profile or not args.label:
        print("Error: --profile and --label are required.", file=sys.stderr)
        sys.exit(1)
    if has_access(args.profile, args.label, base_dir=args.base_dir):
        print(f"'{args.label}' has access to '{args.profile}'.")
    else:
        print(f"'{args.label}' does NOT have access to '{args.profile}'.")
        sys.exit(2)


def register_access_commands(subparsers: argparse._SubParsersAction, base_dir: str | None = None) -> None:  # noqa: SLF001
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--base-dir", default=base_dir)
    common.add_argument("--profile", default=None)
    common.add_argument("--label", default=None)

    subparsers.add_parser("access-grant", parents=[common]).set_defaults(func=cmd_access_grant)
    subparsers.add_parser("access-revoke", parents=[common]).set_defaults(func=cmd_access_revoke)
    subparsers.add_parser("access-list", parents=[common]).set_defaults(func=cmd_access_list)
    subparsers.add_parser("access-show", parents=[common]).set_defaults(func=cmd_access_show_all)
    subparsers.add_parser("access-check", parents=[common]).set_defaults(func=cmd_access_check)
