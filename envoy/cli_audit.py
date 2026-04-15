"""CLI commands for viewing and managing the audit log."""

import argparse
import sys
from typing import Optional

from envoy.audit import read_log, clear_log


def cmd_audit_show(args: argparse.Namespace) -> None:
    """Display audit log entries, optionally filtered by profile."""
    base_dir: Optional[str] = getattr(args, "base_dir", None)
    profile_filter: Optional[str] = getattr(args, "profile", None)

    entries = read_log(base_dir=base_dir)

    if not entries:
        print("No audit log entries found.")
        return

    if profile_filter:
        entries = [e for e in entries if e.get("profile") == profile_filter]
        if not entries:
            print(f"No entries for profile '{profile_filter}'.")
            return

    for entry in entries:
        key_part = f"  key={entry['key']}" if "key" in entry else ""
        print(f"[{entry['timestamp']}] {entry['action']:10s}  profile={entry['profile']}{key_part}")


def cmd_audit_clear(args: argparse.Namespace) -> None:
    """Clear the audit log after confirmation."""
    base_dir: Optional[str] = getattr(args, "base_dir", None)
    force: bool = getattr(args, "force", False)

    if not force:
        answer = input("Clear the entire audit log? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted.")
            return

    clear_log(base_dir=base_dir)
    print("Audit log cleared.")


def register_audit_commands(subparsers) -> None:
    """Register audit sub-commands onto the provided subparsers object."""
    audit_parser = subparsers.add_parser("audit", help="Manage the audit log")
    audit_sub = audit_parser.add_subparsers(dest="audit_cmd")

    show_p = audit_sub.add_parser("show", help="Show audit log")
    show_p.add_argument("--profile", default=None, help="Filter by profile name")
    show_p.set_defaults(func=cmd_audit_show)

    clear_p = audit_sub.add_parser("clear", help="Clear audit log")
    clear_p.add_argument("--force", action="store_true", help="Skip confirmation")
    clear_p.set_defaults(func=cmd_audit_clear)
