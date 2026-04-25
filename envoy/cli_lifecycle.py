"""CLI commands for profile lifecycle management."""

from __future__ import annotations

import sys
from typing import Optional

from envoy.lifecycle import (
    LifecycleError,
    VALID_STATES,
    all_states,
    get_state,
    list_by_state,
    remove_state,
    set_state,
)


def cmd_lifecycle_set(args) -> None:
    """Set the lifecycle state of a profile."""
    try:
        set_state(args.profile, args.state, base_dir=getattr(args, "base_dir", None))
        print(f"Profile '{args.profile}' marked as '{args.state}'.")
    except LifecycleError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_lifecycle_show(args) -> None:
    """Show the lifecycle state of a profile."""
    try:
        state = get_state(args.profile, base_dir=getattr(args, "base_dir", None))
        print(f"{args.profile}: {state}")
    except LifecycleError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_lifecycle_list(args) -> None:
    """List all profiles in a given lifecycle state."""
    try:
        profiles = list_by_state(args.state, base_dir=getattr(args, "base_dir", None))
        if not profiles:
            print(f"No profiles with state '{args.state}'.")
        else:
            for p in profiles:
                print(p)
    except LifecycleError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_lifecycle_all(args) -> None:
    """Show lifecycle states for all profiles that have an explicit state set."""
    states = all_states(base_dir=getattr(args, "base_dir", None))
    if not states:
        print("No lifecycle states recorded.")
    else:
        for profile, state in sorted(states.items()):
            print(f"{profile}: {state}")


def cmd_lifecycle_remove(args) -> None:
    """Remove explicit lifecycle state from a profile (resets to 'active')."""
    remove_state(args.profile, base_dir=getattr(args, "base_dir", None))
    print(f"Lifecycle state removed for '{args.profile}'. Reverted to 'active'.")


def register_lifecycle_commands(subparsers) -> None:
    p = subparsers.add_parser("lifecycle", help="Manage profile lifecycle states")
    sub = p.add_subparsers(dest="lifecycle_cmd", required=True)

    p_set = sub.add_parser("set", help="Set lifecycle state")
    p_set.add_argument("profile")
    p_set.add_argument("state", choices=sorted(VALID_STATES))
    p_set.set_defaults(func=cmd_lifecycle_set)

    p_show = sub.add_parser("show", help="Show lifecycle state of a profile")
    p_show.add_argument("profile")
    p_show.set_defaults(func=cmd_lifecycle_show)

    p_list = sub.add_parser("list", help="List profiles by state")
    p_list.add_argument("state", choices=sorted(VALID_STATES))
    p_list.set_defaults(func=cmd_lifecycle_list)

    p_all = sub.add_parser("all", help="Show all recorded lifecycle states")
    p_all.set_defaults(func=cmd_lifecycle_all)

    p_rm = sub.add_parser("remove", help="Remove lifecycle state from a profile")
    p_rm.add_argument("profile")
    p_rm.set_defaults(func=cmd_lifecycle_remove)
