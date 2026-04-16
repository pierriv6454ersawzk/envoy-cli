"""CLI commands for comparing two envoy profiles."""
from __future__ import annotations
import argparse
import sys
from envoy.compare import compare_profiles, format_compare
from envoy.profile import profile_path, profile_exists


def cmd_compare(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "base_dir", None)

    for name in (args.profile_a, args.profile_b):
        if not profile_exists(name, base_dir=base_dir):
            print(f"[error] Profile '{name}' does not exist.", file=sys.stderr)
            sys.exit(1)

    path_a = profile_path(args.profile_a, base_dir=base_dir)
    path_b = profile_path(args.profile_b, base_dir=base_dir)

    try:
        result = compare_profiles(
            path_a, args.passphrase_a,
            path_b, args.passphrase_b,
        )
    except ValueError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)

    show_same = getattr(args, "show_same", False)
    mask = not getattr(args, "reveal", False)
    output = format_compare(result, show_same=show_same, mask=mask)
    print(f"Comparing '{args.profile_a}' (<) vs '{args.profile_b}' (>):")
    print(output)


def register_compare_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("compare", help="Compare two profiles side-by-side")
    p.add_argument("profile_a", help="First profile name")
    p.add_argument("profile_b", help="Second profile name")
    p.add_argument("--passphrase-a", required=True, dest="passphrase_a", help="Passphrase for first profile")
    p.add_argument("--passphrase-b", required=True, dest="passphrase_b", help="Passphrase for second profile")
    p.add_argument("--show-same", action="store_true", help="Also show identical keys")
    p.add_argument("--reveal", action="store_true", help="Show actual values instead of masking")
    p.set_defaults(func=cmd_compare)
