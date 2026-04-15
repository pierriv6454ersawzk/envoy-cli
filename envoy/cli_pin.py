"""CLI commands for managing profile pins."""

from __future__ import annotations

import argparse
import sys

from envoy.pin import get_pin, list_pins, pin_profile, unpin_profile


def cmd_pin_set(args: argparse.Namespace) -> None:
    """Pin a profile to a snapshot ID."""
    pin_profile(args.profile, args.snapshot_id, base_dir=args.base_dir)
    print(f"Pinned '{args.profile}' to snapshot '{args.snapshot_id}'.")


def cmd_pin_remove(args: argparse.Namespace) -> None:
    """Remove the pin from a profile."""
    try:
        unpin_profile(args.profile, base_dir=args.base_dir)
        print(f"Unpinned '{args.profile}'.")
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_pin_show(args: argparse.Namespace) -> None:
    """Show the snapshot ID pinned to a profile."""
    snapshot_id = get_pin(args.profile, base_dir=args.base_dir)
    if snapshot_id is None:
        print(f"Profile '{args.profile}' is not pinned.")
    else:
        print(f"{args.profile} -> {snapshot_id}")


def cmd_pin_list(args: argparse.Namespace) -> None:
    """List all pinned profiles."""
    pins = list_pins(base_dir=args.base_dir)
    if not pins:
        print("No profiles are pinned.")
        return
    for profile, snapshot_id in sorted(pins.items()):
        print(f"{profile:<20} {snapshot_id}")


def register_pin_commands(subparsers: argparse._SubParsersAction, base_dir: str = None) -> None:
    pin_parser = subparsers.add_parser("pin", help="Manage profile snapshot pins")
    pin_sub = pin_parser.add_subparsers(dest="pin_cmd")

    p_set = pin_sub.add_parser("set", help="Pin a profile to a snapshot")
    p_set.add_argument("profile")
    p_set.add_argument("snapshot_id")
    p_set.set_defaults(func=cmd_pin_set, base_dir=base_dir)

    p_remove = pin_sub.add_parser("remove", help="Unpin a profile")
    p_remove.add_argument("profile")
    p_remove.set_defaults(func=cmd_pin_remove, base_dir=base_dir)

    p_show = pin_sub.add_parser("show", help="Show pin for a profile")
    p_show.add_argument("profile")
    p_show.set_defaults(func=cmd_pin_show, base_dir=base_dir)

    p_list = pin_sub.add_parser("list", help="List all pinned profiles")
    p_list.set_defaults(func=cmd_pin_list, base_dir=base_dir)
