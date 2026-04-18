"""CLI commands for profile priority management."""

import sys
from envoy.priority import set_priority, remove_priority, get_priority, list_priorities, PriorityError


def cmd_priority_set(args):
    try:
        priority = int(args.priority)
    except (ValueError, TypeError):
        print("Error: priority must be an integer.", file=sys.stderr)
        sys.exit(1)
    try:
        set_priority(args.base_dir, args.profile, priority)
        print(f"Priority for '{args.profile}' set to {priority}.")
    except PriorityError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_priority_remove(args):
    remove_priority(args.base_dir, args.profile)
    print(f"Priority for '{args.profile}' removed.")


def cmd_priority_show(args):
    p = get_priority(args.base_dir, args.profile)
    print(f"{args.profile}: {p}")


def cmd_priority_list(args):
    entries = list_priorities(args.base_dir)
    if not entries:
        print("No priorities set.")
        return
    for profile, priority in entries:
        print(f"{profile}: {priority}")


def register_priority_commands(subparsers, base_dir):
    p = subparsers.add_parser("priority", help="Manage profile priorities")
    sub = p.add_subparsers(dest="priority_cmd")

    ps = sub.add_parser("set")
    ps.add_argument("profile")
    ps.add_argument("priority", type=int)
    ps.set_defaults(func=cmd_priority_set, base_dir=base_dir)

    pr = sub.add_parser("remove")
    pr.add_argument("profile")
    pr.set_defaults(func=cmd_priority_remove, base_dir=base_dir)

    psh = sub.add_parser("show")
    psh.add_argument("profile")
    psh.set_defaults(func=cmd_priority_show, base_dir=base_dir)

    pl = sub.add_parser("list")
    pl.set_defaults(func=cmd_priority_list, base_dir=base_dir)
