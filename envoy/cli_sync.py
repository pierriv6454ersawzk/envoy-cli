"""CLI commands for sync operations (push, pull, diff, remote config)."""

import sys
from typing import Optional

from envoy.sync import (
    push_profile,
    pull_profile,
    diff_profiles,
    get_remote_config,
    set_remote_config,
)


def cmd_push(args) -> None:
    """Push a local profile to a remote path."""
    try:
        push_profile(
            profile=args.profile,
            passphrase=args.passphrase,
            remote_path=args.remote,
            base_dir=getattr(args, "base_dir", None),
        )
        print(f"Pushed profile '{args.profile}' -> {args.remote}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_pull(args) -> None:
    """Pull a remote profile into the local vault."""
    try:
        pull_profile(
            profile=args.profile,
            passphrase=args.passphrase,
            remote_path=args.remote,
            base_dir=getattr(args, "base_dir", None),
        )
        print(f"Pulled '{args.remote}' -> profile '{args.profile}'")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_diff(args) -> None:
    """Show differences between a local profile and a remote vault file."""
    try:
        diff = diff_profiles(
            profile=args.profile,
            passphrase=args.passphrase,
            remote_path=args.remote,
            base_dir=getattr(args, "base_dir", None),
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not diff:
        print("No differences found.")
        return

    print(f"{'KEY':<20} {'LOCAL':<20} {'REMOTE':<20}")
    print("-" * 62)
    for key, vals in sorted(diff.items()):
        local_val = vals["local"] if vals["local"] is not None else "(missing)"
        remote_val = vals["remote"] if vals["remote"] is not None else "(missing)"
        print(f"{key:<20} {local_val:<20} {remote_val:<20}")


def cmd_remote_set(args) -> None:
    """Store a remote backend configuration key."""
    base_dir = getattr(args, "base_dir", None)
    config = get_remote_config(base_dir)
    config[args.key] = args.value
    set_remote_config(config, base_dir)
    print(f"Remote config: {args.key} = {args.value}")


def cmd_remote_show(args) -> None:
    """Display the current remote backend configuration."""
    base_dir = getattr(args, "base_dir", None)
    config = get_remote_config(base_dir)
    if not config:
        print("No remote configuration found.")
        return
    for k, v in config.items():
        print(f"{k}={v}")
