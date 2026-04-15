"""CLI commands for profile alias management."""

from __future__ import annotations

import argparse
import sys

from envoy.alias import add_alias, remove_alias, resolve_alias, list_aliases


def cmd_alias_add(args: argparse.Namespace) -> None:
    """envoy alias add <alias> <profile>"""
    try:
        add_alias(args.alias, args.profile, base_dir=args.base_dir)
        print(f"Alias '{args.alias}' -> '{args.profile}' added.")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_alias_remove(args: argparse.Namespace) -> None:
    """envoy alias remove <alias>"""
    try:
        remove_alias(args.alias, base_dir=args.base_dir)
        print(f"Alias '{args.alias}' removed.")
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_alias_show(args: argparse.Namespace) -> None:
    """envoy alias show <alias>"""
    profile = resolve_alias(args.alias, base_dir=args.base_dir)
    if profile is None:
        print(f"No alias named '{args.alias}'.", file=sys.stderr)
        sys.exit(1)
    print(profile)


def cmd_alias_list(args: argparse.Namespace) -> None:
    """envoy alias list"""
    aliases = list_aliases(base_dir=args.base_dir)
    if not aliases:
        print("No aliases defined.")
        return
    width = max(len(k) for k in aliases)
    for alias, profile in sorted(aliases.items()):
        print(f"  {alias:<{width}}  ->  {profile}")


def register_alias_commands(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    alias_parser = subparsers.add_parser("alias", help="Manage profile aliases")
    alias_sub = alias_parser.add_subparsers(dest="alias_cmd", required=True)

    p_add = alias_sub.add_parser("add", help="Add or update an alias")
    p_add.add_argument("alias")
    p_add.add_argument("profile")
    p_add.set_defaults(func=cmd_alias_add)

    p_remove = alias_sub.add_parser("remove", help="Remove an alias")
    p_remove.add_argument("alias")
    p_remove.set_defaults(func=cmd_alias_remove)

    p_show = alias_sub.add_parser("show", help="Resolve an alias to its profile")
    p_show.add_argument("alias")
    p_show.set_defaults(func=cmd_alias_show)

    p_list = alias_sub.add_parser("list", help="List all aliases")
    p_list.set_defaults(func=cmd_alias_list)
