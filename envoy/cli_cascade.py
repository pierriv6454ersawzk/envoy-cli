"""CLI commands for cascade profile resolution."""
from __future__ import annotations
import sys
from envoy.cascade import resolve_cascade, cascade_sources, CascadeError


def cmd_cascade_resolve(args) -> None:
    """Print merged env vars from a cascade of profiles."""
    profiles = args.profiles
    if not profiles:
        print("Error: at least one profile required.", file=sys.stderr)
        sys.exit(1)
    try:
        merged = resolve_cascade(profiles, args.passphrase, base_dir=getattr(args, "base_dir", None))
    except CascadeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    for k, v in sorted(merged.items()):
        print(f"{k}={v}")


def cmd_cascade_sources(args) -> None:
    """Show each key, its value, and which profile it came from."""
    profiles = args.profiles
    if not profiles:
        print("Error: at least one profile required.", file=sys.stderr)
        sys.exit(1)
    try:
        sources = cascade_sources(profiles, args.passphrase, base_dir=getattr(args, "base_dir", None))
    except CascadeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    for k, (v, profile) in sorted(sources.items()):
        print(f"{k}={v}  [{profile}]")


def register_cascade_commands(subparsers, common_args) -> None:
    p_resolve = subparsers.add_parser("cascade-resolve", help="Merge profiles and print result")
    common_args(p_resolve)
    p_resolve.add_argument("profiles", nargs="+", help="Profiles to merge, left-to-right")
    p_resolve.set_defaults(func=cmd_cascade_resolve)

    p_sources = subparsers.add_parser("cascade-sources", help="Show each key's winning profile")
    common_args(p_sources)
    p_sources.add_argument("profiles", nargs="+", help="Profiles to merge, left-to-right")
    p_sources.set_defaults(func=cmd_cascade_sources)
