"""CLI commands for merging profiles."""
import argparse
import sys
from envoy.merge import merge_profiles, MergeError


def cmd_merge(args: argparse.Namespace) -> None:
    sources = args.sources
    target = args.target
    passphrase = args.passphrase
    base_dir = getattr(args, "base_dir", None)
    no_overwrite = getattr(args, "no_overwrite", False)

    if not sources:
        print("Error: at least one source profile required.", file=sys.stderr)
        sys.exit(1)

    try:
        stats = merge_profiles(
            sources=sources,
            target=target,
            passphrase=passphrase,
            base_dir=base_dir,
            overwrite=not no_overwrite,
        )
    except MergeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    for source, count in stats.items():
        print(f"Merged {count} key(s) from '{source}' into '{target}'.")


def register_merge_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "merge",
        help="Merge keys from one or more profiles into a target profile.",
    )
    parser.add_argument("target", help="Target profile name.")
    parser.add_argument("sources", nargs="+", help="Source profile name(s).")
    parser.add_argument("--passphrase", required=True, help="Vault passphrase.")
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Do not overwrite existing keys in target.",
    )
    parser.set_defaults(func=cmd_merge)
