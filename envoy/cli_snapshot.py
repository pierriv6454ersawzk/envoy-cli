"""CLI commands for snapshot management."""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Any

from envoy.snapshot import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)


def cmd_snapshot_create(args: Any) -> None:
    """envoy snapshot create <profile> --passphrase <p> [--label <l>]"""
    try:
        sid = create_snapshot(
            args.profile,
            args.passphrase,
            label=getattr(args, "label", None),
            base_dir=getattr(args, "base_dir", None),
        )
        print(f"Snapshot created: {sid}")
    except FileNotFoundError:
        print(f"Error: profile '{args.profile}' does not exist.", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_snapshot_list(args: Any) -> None:
    """envoy snapshot list [--profile <p>]"""
    profile = getattr(args, "profile", None)
    entries = list_snapshots(profile=profile, base_dir=getattr(args, "base_dir", None))
    if not entries:
        print("No snapshots found.")
        return
    for e in entries:
        ts = datetime.fromtimestamp(e["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        label = f"  [{e['label']}]" if e["label"] else ""
        print(f"{e['id']}{label}  profile={e['profile']}  {ts}")


def cmd_snapshot_restore(args: Any) -> None:
    """envoy snapshot restore <snapshot_id> --passphrase <p> [--profile <p>]"""
    target = getattr(args, "profile", None)
    try:
        dest = restore_snapshot(
            args.snapshot_id,
            args.passphrase,
            target_profile=target,
            base_dir=getattr(args, "base_dir", None),
        )
        print(f"Restored snapshot '{args.snapshot_id}' into profile '{dest}'.")
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_snapshot_delete(args: Any) -> None:
    """envoy snapshot delete <snapshot_id>"""
    try:
        delete_snapshot(
            args.snapshot_id,
            base_dir=getattr(args, "base_dir", None),
        )
        print(f"Snapshot '{args.snapshot_id}' deleted.")
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_snapshot_commands(subparsers: Any) -> None:
    snap = subparsers.add_parser("snapshot", help="Manage env snapshots")
    sub = snap.add_subparsers(dest="snapshot_cmd")

    p_create = sub.add_parser("create", help="Create a snapshot of a profile")
    p_create.add_argument("profile")
    p_create.add_argument("--passphrase", required=True)
    p_create.add_argument("--label", default="")
    p_create.set_defaults(func=cmd_snapshot_create)

    p_list = sub.add_parser("list", help="List snapshots")
    p_list.add_argument("--profile", default=None)
    p_list.set_defaults(func=cmd_snapshot_list)

    p_restore = sub.add_parser("restore", help="Restore a snapshot")
    p_restore.add_argument("snapshot_id")
    p_restore.add_argument("--passphrase", required=True)
    p_restore.add_argument("--profile", default=None)
    p_restore.set_defaults(func=cmd_snapshot_restore)

    p_delete = sub.add_parser("delete", help="Delete a snapshot")
    p_delete.add_argument("snapshot_id")
    p_delete.set_defaults(func=cmd_snapshot_delete)
