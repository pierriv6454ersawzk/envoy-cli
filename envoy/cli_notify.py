"""CLI commands for managing envoy notifications."""
from __future__ import annotations
import argparse
import sys
from envoy import notify
from envoy.profile import get_vault_dir


def cmd_notify_add(args: argparse.Namespace) -> None:
    base_dir = get_vault_dir(args)
    try:
        notify.set_notify(base_dir, args.event, args.channel, args.target)
        print(f"Notification added: {args.event} -> {args.channel}" + (f" ({args.target})" if args.target else ""))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_notify_remove(args: argparse.Namespace) -> None:
    base_dir = get_vault_dir(args)
    removed = notify.remove_notify(base_dir, args.event, args.channel)
    if removed:
        print(f"Notification removed: {args.event} -> {args.channel}")
    else:
        print(f"No matching notification found for event '{args.event}' channel '{args.channel}'.")


def cmd_notify_list(args: argparse.Namespace) -> None:
    base_dir = get_vault_dir(args)
    event = getattr(args, "event", None)
    config = notify.list_notify(base_dir, event)
    if not any(config.values()):
        print("No notifications configured.")
        return
    for ev, entries in config.items():
        for entry in entries:
            target = entry.get("target") or ""
            print(f"  {ev:20s} {entry['channel']:10s} {target}")


def cmd_notify_dispatch(args: argparse.Namespace) -> None:
    base_dir = get_vault_dir(args)
    dispatched = notify.dispatch(base_dir, args.event, args.message)
    if dispatched:
        print(f"Dispatched to: {', '.join(dispatched)}")
    else:
        print("No notifications dispatched.")


def register_notify_commands(subparsers) -> None:
    p = subparsers.add_parser("notify", help="Manage notifications")
    sub = p.add_subparsers(dest="notify_cmd")

    add_p = sub.add_parser("add", help="Add a notification")
    add_p.add_argument("event")
    add_p.add_argument("channel", choices=notify.VALID_CHANNELS)
    add_p.add_argument("--target", default=None)
    add_p.set_defaults(func=cmd_notify_add)

    rm_p = sub.add_parser("remove", help="Remove a notification")
    rm_p.add_argument("event")
    rm_p.add_argument("channel")
    rm_p.set_defaults(func=cmd_notify_remove)

    ls_p = sub.add_parser("list", help="List notifications")
    ls_p.add_argument("--event", default=None)
    ls_p.set_defaults(func=cmd_notify_list)

    dp_p = sub.add_parser("dispatch", help="Manually dispatch a notification")
    dp_p.add_argument("event")
    dp_p.add_argument("message")
    dp_p.set_defaults(func=cmd_notify_dispatch)
