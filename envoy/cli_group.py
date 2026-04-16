"""CLI commands for group management."""
from __future__ import annotations
import argparse
import sys
from envoy.group import (
    add_to_group, remove_from_group, list_groups,
    group_members, delete_group, profile_groups,
)


def cmd_group_add(args: argparse.Namespace) -> None:
    try:
        add_to_group(args.group, args.profile, base_dir=args.base_dir)
        print(f"Profile '{args.profile}' added to group '{args.group}'.")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_group_remove(args: argparse.Namespace) -> None:
    remove_from_group(args.group, args.profile, base_dir=args.base_dir)
    print(f"Profile '{args.profile}' removed from group '{args.group}'.")


def cmd_group_list(args: argparse.Namespace) -> None:
    groups = list_groups(base_dir=args.base_dir)
    if not groups:
        print("No groups defined.")
    else:
        for g in groups:
            print(g)


def cmd_group_members(args: argparse.Namespace) -> None:
    members = group_members(args.group, base_dir=args.base_dir)
    if not members:
        print(f"Group '{args.group}' is empty or does not exist.")
    else:
        for m in members:
            print(m)


def cmd_group_delete(args: argparse.Namespace) -> None:
    delete_group(args.group, base_dir=args.base_dir)
    print(f"Group '{args.group}' deleted.")


def cmd_group_show(args: argparse.Namespace) -> None:
    groups = profile_groups(args.profile, base_dir=args.base_dir)
    if not groups:
        print(f"Profile '{args.profile}' is not in any group.")
    else:
        for g in groups:
            print(g)


def register_group_commands(subparsers, common_parents: list) -> None:
    p = subparsers.add_parser("group", help="Manage profile groups")
    sp = p.add_subparsers(dest="group_cmd", required=True)

    add_p = sp.add_parser("add", parents=common_parents)
    add_p.add_argument("group")
    add_p.add_argument("profile")
    add_p.set_defaults(func=cmd_group_add)

    rem_p = sp.add_parser("remove", parents=common_parents)
    rem_p.add_argument("group")
    rem_p.add_argument("profile")
    rem_p.set_defaults(func=cmd_group_remove)

    lst_p = sp.add_parser("list", parents=common_parents)
    lst_p.set_defaults(func=cmd_group_list)

    mem_p = sp.add_parser("members", parents=common_parents)
    mem_p.add_argument("group")
    mem_p.set_defaults(func=cmd_group_members)

    del_p = sp.add_parser("delete", parents=common_parents)
    del_p.add_argument("group")
    del_p.set_defaults(func=cmd_group_delete)

    show_p = sp.add_parser("show", parents=common_parents)
    show_p.add_argument("profile")
    show_p.set_defaults(func=cmd_group_show)
