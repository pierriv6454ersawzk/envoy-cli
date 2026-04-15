"""CLI commands for managing envoy hooks."""

import argparse
import sys

from envoy.hook import HOOK_EVENTS, add_hook, list_hooks, remove_hook, run_hooks
from envoy.profile import get_vault_dir


def cmd_hook_add(args: argparse.Namespace) -> None:
    base_dir = get_vault_dir(args.base_dir)
    try:
        add_hook(base_dir, args.event, args.command)
        print(f"Hook registered: [{args.event}] -> {args.command!r}")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_hook_remove(args: argparse.Namespace) -> None:
    base_dir = get_vault_dir(args.base_dir)
    removed = remove_hook(base_dir, args.event, args.command)
    if removed:
        print(f"Hook removed: [{args.event}] -> {args.command!r}")
    else:
        print(f"Hook not found: [{args.event}] -> {args.command!r}", file=sys.stderr)
        sys.exit(1)


def cmd_hook_list(args: argparse.Namespace) -> None:
    base_dir = get_vault_dir(args.base_dir)
    event_filter = getattr(args, "event", None)
    hooks = list_hooks(base_dir, event_filter)
    if not any(hooks.values()):
        print("No hooks registered.")
        return
    for event, cmds in hooks.items():
        for cmd in cmds:
            print(f"  [{event}] {cmd}")


def cmd_hook_run(args: argparse.Namespace) -> None:
    base_dir = get_vault_dir(args.base_dir)
    if args.event not in HOOK_EVENTS:
        print(f"Error: Unknown event '{args.event}'", file=sys.stderr)
        sys.exit(1)
    codes = run_hooks(base_dir, args.event)
    if codes:
        print(f"Ran {len(codes)} hook(s) for event '{args.event}'.")
    else:
        print(f"No hooks registered for event '{args.event}'.")


def register_hook_commands(subparsers, common_args) -> None:
    hook_parser = subparsers.add_parser("hook", help="Manage lifecycle hooks")
    hook_sub = hook_parser.add_subparsers(dest="hook_cmd", required=True)

    p_add = hook_sub.add_parser("add", help="Register a hook")
    p_add.add_argument("event", choices=HOOK_EVENTS)
    p_add.add_argument("command", help="Shell command to run")
    common_args(p_add)
    p_add.set_defaults(func=cmd_hook_add)

    p_rm = hook_sub.add_parser("remove", help="Remove a hook")
    p_rm.add_argument("event", choices=HOOK_EVENTS)
    p_rm.add_argument("command", help="Shell command to remove")
    common_args(p_rm)
    p_rm.set_defaults(func=cmd_hook_remove)

    p_ls = hook_sub.add_parser("list", help="List registered hooks")
    p_ls.add_argument("--event", choices=HOOK_EVENTS, default=None)
    common_args(p_ls)
    p_ls.set_defaults(func=cmd_hook_list)

    p_run = hook_sub.add_parser("run", help="Manually trigger hooks for an event")
    p_run.add_argument("event", choices=HOOK_EVENTS)
    common_args(p_run)
    p_run.set_defaults(func=cmd_hook_run)
