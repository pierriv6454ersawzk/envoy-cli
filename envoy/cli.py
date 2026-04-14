"""Command-line interface for envoy-cli."""

import sys
import os
import argparse
from getpass import getpass

from envoy.vault import save, load


def cmd_set(args):
    """Set one or more key=value pairs in the vault."""
    passphrase = getpass("Passphrase: ")

    # Load existing env or start fresh
    try:
        env = load(args.file, passphrase)
    except FileNotFoundError:
        env = {}

    for pair in args.pairs:
        if "=" not in pair:
            print(f"Error: '{pair}' is not a valid key=value pair.", file=sys.stderr)
            sys.exit(1)
        key, _, value = pair.partition("=")
        env[key.strip()] = value.strip()

    save(args.file, env, passphrase)
    print(f"Saved {len(args.pairs)} variable(s) to '{args.file}'.")


def cmd_get(args):
    """Get the value of a key from the vault."""
    passphrase = getpass("Passphrase: ")

    try:
        env = load(args.file, passphrase)
    except FileNotFoundError:
        print(f"Error: vault file '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)

    if args.key not in env:
        print(f"Error: key '{args.key}' not found.", file=sys.stderr)
        sys.exit(1)

    print(env[args.key])


def cmd_list(args):
    """List all keys in the vault."""
    passphrase = getpass("Passphrase: ")

    try:
        env = load(args.file, passphrase)
    except FileNotFoundError:
        print(f"Error: vault file '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)

    if not env:
        print("(empty)")
    else:
        for key, value in sorted(env.items()):
            print(f"{key}={value}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envoy",
        description="Manage and sync encrypted .env files.",
    )
    parser.add_argument(
        "--file", "-f",
        default=".env.vault",
        help="Path to the vault file (default: .env.vault)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # set command
    set_parser = subparsers.add_parser("set", help="Set key=value pairs in the vault.")
    set_parser.add_argument("pairs", nargs="+", metavar="KEY=VALUE")
    set_parser.set_defaults(func=cmd_set)

    # get command
    get_parser = subparsers.add_parser("get", help="Get a value from the vault.")
    get_parser.add_argument("key", metavar="KEY")
    get_parser.set_defaults(func=cmd_get)

    # list command
    list_parser = subparsers.add_parser("list", help="List all keys in the vault.")
    list_parser.set_defaults(func=cmd_list)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
