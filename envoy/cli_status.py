"""CLI command: envoy status."""
from __future__ import annotations
import argparse
import sys

from envoy.status import get_status, format_status
from envoy.profile import get_vault_dir


def cmd_status(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "base_dir", None)
    profile = getattr(args, "profile", "default")
    passphrase = getattr(args, "passphrase", "")

    try:
        s = get_status(profile, passphrase, base_dir=base_dir)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(format_status(s))
    if s.is_expired:
        sys.exit(2)


def register_status_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("status", help="Show status summary for a profile")
    p.add_argument("--profile", default="default", help="Profile name")
    p.add_argument("--passphrase", default="", help="Vault passphrase")
    p.set_defaults(func=cmd_status)
