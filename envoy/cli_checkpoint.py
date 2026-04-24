"""CLI commands for checkpoint management."""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Any

from envoy.checkpoint import (
    CheckpointError,
    create_checkpoint,
    delete_checkpoint,
    list_checkpoints,
    restore_checkpoint,
)


def cmd_checkpoint_create(args: Any) -> None:
    """envoy checkpoint create <profile> <name> --passphrase <p>"""
    try:
        create_checkpoint(args.profile, args.passphrase, args.name, args.base_dir)
        print(f"Checkpoint '{args.name}' created for profile '{args.profile}'.")
    except CheckpointError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_checkpoint_list(args: Any) -> None:
    """envoy checkpoint list <profile>"""
    entries = list_checkpoints(args.profile, args.base_dir)
    if not entries:
        print(f"No checkpoints for profile '{args.profile}'.")
        return
    for entry in entries:
        ts = datetime.fromtimestamp(entry["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {entry['name']:<24}  keys={entry['key_count']}  created={ts}")


def cmd_checkpoint_restore(args: Any) -> None:
    """envoy checkpoint restore <profile> <name> --passphrase <p>"""
    try:
        restore_checkpoint(args.profile, args.name, args.passphrase, args.base_dir)
        print(f"Profile '{args.profile}' restored from checkpoint '{args.name}'.")
    except CheckpointError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_checkpoint_delete(args: Any) -> None:
    """envoy checkpoint delete <profile> <name>"""
    try:
        delete_checkpoint(args.profile, args.name, args.base_dir)
        print(f"Checkpoint '{args.name}' deleted from profile '{args.profile}'.")
    except CheckpointError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_checkpoint_commands(subparsers: Any) -> None:
    p = subparsers.add_parser("checkpoint", help="Manage named env checkpoints")
    sp = p.add_subparsers(dest="checkpoint_cmd", required=True)

    c = sp.add_parser("create", help="Create a checkpoint")
    c.add_argument("profile")
    c.add_argument("name")
    c.add_argument("--passphrase", required=True)
    c.set_defaults(func=cmd_checkpoint_create)

    ls = sp.add_parser("list", help="List checkpoints for a profile")
    ls.add_argument("profile")
    ls.set_defaults(func=cmd_checkpoint_list)

    r = sp.add_parser("restore", help="Restore a checkpoint")
    r.add_argument("profile")
    r.add_argument("name")
    r.add_argument("--passphrase", required=True)
    r.set_defaults(func=cmd_checkpoint_restore)

    d = sp.add_parser("delete", help="Delete a checkpoint")
    d.add_argument("profile")
    d.add_argument("name")
    d.set_defaults(func=cmd_checkpoint_delete)
