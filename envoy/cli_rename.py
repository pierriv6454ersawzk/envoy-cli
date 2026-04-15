"""CLI commands for renaming keys inside a profile vault."""

from __future__ import annotations

import argparse
import sys

from envoy.rename import rename_key, RenameError


def cmd_rename(args: argparse.Namespace) -> None:
    """Rename a key inside a profile vault."""
    try:
        rename_key(
            profile=args.profile,
            old_key=args.old_key,
            new_key=args.new_key,
            passphrase=args.passphrase,
            base_dir=getattr(args, "base_dir", None),
            overwrite=args.overwrite,
        )
    except RenameError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        # Wrong passphrase / corrupted vault
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(
        f"Renamed '{args.old_key}' → '{args.new_key}' "
        f"in profile '{args.profile}'."
    )


def register_rename_commands(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    """Attach the *rename* sub-command to *subparsers*."""
    parser = subparsers.add_parser(
        "rename",
        help="Rename a key inside a profile vault",
    )
    parser.add_argument("profile", help="Target profile name")
    parser.add_argument("old_key", help="Existing key name")
    parser.add_argument("new_key", help="New key name")
    parser.add_argument("--passphrase", required=True, help="Vault passphrase")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite new_key if it already exists",
    )
    parser.set_defaults(func=cmd_rename)
