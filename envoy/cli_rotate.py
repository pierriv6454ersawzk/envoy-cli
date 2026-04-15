"""CLI commands for key rotation."""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

from envoy.rotate import rotate_key


def cmd_rotate(args: argparse.Namespace) -> None:
    """Rotate the encryption key for a vault profile."""
    base_dir: Path | None = Path(args.base_dir) if getattr(args, "base_dir", None) else None
    profile: str = args.profile

    # Prompt for passphrases when not supplied (e.g. in tests they are injected)
    old_passphrase: str = getattr(args, "old_passphrase", None) or getpass.getpass(
        f"Current passphrase for profile '{profile}': "
    )
    new_passphrase: str = getattr(args, "new_passphrase", None) or getpass.getpass(
        "New passphrase: "
    )
    confirm: str = getattr(args, "confirm_passphrase", None) or getpass.getpass(
        "Confirm new passphrase: "
    )

    if new_passphrase != confirm:
        print("Error: new passphrases do not match.", file=sys.stderr)
        sys.exit(1)

    try:
        rotate_key(profile, old_passphrase, new_passphrase, base_dir=base_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Error: incorrect current passphrase.", file=sys.stderr)
        sys.exit(1)

    print(f"Key rotated successfully for profile '{profile}'.")


def register_rotate_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Attach the *rotate* sub-command to *subparsers*."""
    p = subparsers.add_parser("rotate", help="Re-encrypt a profile under a new passphrase")
    p.add_argument("profile", nargs="?", default="default", help="Profile name (default: default)")
    p.set_defaults(func=cmd_rotate)
