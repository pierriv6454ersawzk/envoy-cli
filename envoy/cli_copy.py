"""CLI commands for copying variables between profiles."""

from __future__ import annotations

import argparse
import sys

from envoy.copy import copy_keys


def cmd_copy(args: argparse.Namespace) -> None:
    """Handle the `envoy copy` command."""
    keys = args.keys if args.keys else None

    src_pass = args.src_passphrase
    dst_pass = args.dst_passphrase if args.dst_passphrase else src_pass

    try:
        copied = copy_keys(
            src_profile=args.src,
            dst_profile=args.dst,
            src_passphrase=src_pass,
            dst_passphrase=dst_pass,
            keys=keys,
            overwrite=not args.no_overwrite,
            base_dir=getattr(args, "base_dir", None),
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Copied {len(copied)} key(s) from '{args.src}' → '{args.dst}':")
    for k in copied:
        print(f"  {k}")


def register_copy_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the `copy` sub-command."""
    p = subparsers.add_parser(
        "copy",
        help="Copy environment variables from one profile to another.",
    )
    p.add_argument("src", help="Source profile name.")
    p.add_argument("dst", help="Destination profile name.")
    p.add_argument(
        "--src-passphrase",
        required=True,
        dest="src_passphrase",
        help="Passphrase for the source vault.",
    )
    p.add_argument(
        "--dst-passphrase",
        dest="dst_passphrase",
        default=None,
        help="Passphrase for the destination vault (defaults to src passphrase).",
    )
    p.add_argument(
        "keys",
        nargs="*",
        help="Specific keys to copy (omit to copy all).",
    )
    p.add_argument(
        "--no-overwrite",
        action="store_true",
        default=False,
        help="Skip keys that already exist in the destination.",
    )
    p.set_defaults(func=cmd_copy)
