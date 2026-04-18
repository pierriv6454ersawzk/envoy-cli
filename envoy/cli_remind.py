"""CLI commands for managing reminders."""
from __future__ import annotations
import sys
import time
from envoy.remind import set_reminder, remove_reminder, get_reminder, list_reminders, due_reminders, ReminderError


def cmd_remind_set(args) -> None:
    try:
        due = float(args.due)
    except ValueError:
        print("Error: --due must be a Unix timestamp (float).", file=sys.stderr)
        sys.exit(1)
    try:
        set_reminder(args.base_dir, args.profile, args.key, args.message, due)
        print(f"Reminder set for '{args.key}' in profile '{args.profile}'.")
    except ReminderError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_remind_remove(args) -> None:
    removed = remove_reminder(args.base_dir, args.profile, args.key)
    if removed:
        print(f"Reminder for '{args.key}' removed from profile '{args.profile}'.")
    else:
        print(f"No reminder found for '{args.key}' in profile '{args.profile}'.")


def cmd_remind_show(args) -> None:
    r = get_reminder(args.base_dir, args.profile, args.key)
    if r is None:
        print(f"No reminder set for '{args.key}'.")
    else:
        due_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r["due"]))
        print(f"Key:     {args.key}")
        print(f"Message: {r['message']}")
        print(f"Due:     {due_str}")


def cmd_remind_list(args) -> None:
    reminders = list_reminders(args.base_dir, args.profile)
    if not reminders:
        print(f"No reminders for profile '{args.profile}'.")
        return
    for key, r in reminders.items():
        due_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r["due"]))
        print(f"  {key}: {r['message']} (due {due_str})")


def cmd_remind_due(args) -> None:
    overdue = due_reminders(args.base_dir, args.profile)
    if not overdue:
        print(f"No due reminders for profile '{args.profile}'.")
        return
    for key, r in overdue.items():
        print(f"  [DUE] {key}: {r['message']}")


def register_remind_commands(subparsers, common_args):
    p = subparsers.add_parser("remind-set", parents=[common_args])
    p.add_argument("profile"); p.add_argument("key"); p.add_argument("message"); p.add_argument("--due", required=True)
    p.set_defaults(func=cmd_remind_set)

    p = subparsers.add_parser("remind-remove", parents=[common_args])
    p.add_argument("profile"); p.add_argument("key")
    p.set_defaults(func=cmd_remind_remove)

    p = subparsers.add_parser("remind-show", parents=[common_args])
    p.add_argument("profile"); p.add_argument("key")
    p.set_defaults(func=cmd_remind_show)

    p = subparsers.add_parser("remind-list", parents=[common_args])
    p.add_argument("profile")
    p.set_defaults(func=cmd_remind_list)

    p = subparsers.add_parser("remind-due", parents=[common_args])
    p.add_argument("profile")
    p.set_defaults(func=cmd_remind_due)
