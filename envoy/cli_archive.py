"""CLI commands for vault archiving."""

import sys
from envoy.archive import create_archive, list_archives, restore_archive, delete_archive
import time


def cmd_archive_create(args):
    label = getattr(args, "label", "") or ""
    path = create_archive(args.base_dir, label=label)
    print(f"Archive created: {path.name}")


def cmd_archive_list(args):
    entries = list_archives(args.base_dir)
    if not entries:
        print("No archives found.")
        return
    for e in entries:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e["timestamp"]))
        label = f"  [{e['label']}]" if e.get("label") else ""
        print(f"{e['file']}  {ts}{label}")


def cmd_archive_restore(args):
    if not args.name:
        print("Error: archive name required.", file=sys.stderr)
        sys.exit(1)
    try:
        restore_archive(args.base_dir, args.name)
        print(f"Restored from archive: {args.name}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_archive_delete(args):
    if not args.name:
        print("Error: archive name required.", file=sys.stderr)
        sys.exit(1)
    deleted = delete_archive(args.base_dir, args.name)
    if deleted:
        print(f"Deleted archive: {args.name}")
    else:
        print(f"Archive not found: {args.name}", file=sys.stderr)
        sys.exit(1)


def register_archive_commands(subparsers):
    p = subparsers.add_parser("archive", help="Manage vault archives")
    sub = p.add_subparsers(dest="archive_cmd")

    pc = sub.add_parser("create", help="Create a new archive")
    pc.add_argument("--label", default="", help="Optional label")
    pc.set_defaults(func=cmd_archive_create)

    pl = sub.add_parser("list", help="List archives")
    pl.set_defaults(func=cmd_archive_list)

    pr = sub.add_parser("restore", help="Restore from archive")
    pr.add_argument("name", help="Archive filename")
    pr.set_defaults(func=cmd_archive_restore)

    pd = sub.add_parser("delete", help="Delete an archive")
    pd.add_argument("name", help="Archive filename")
    pd.set_defaults(func=cmd_archive_delete)
