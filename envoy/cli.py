"""CLI entry point for envoy-cli."""

import argparse
import sys

from envoy import vault
from envoy.profile import (
    profile_path,
    list_profiles,
    profile_exists,
    delete_profile,
    DEFAULT_PROFILE,
)


def cmd_set(args):
    pairs = {}
    for pair in args.pairs:
        if "=" not in pair:
            print(f"Error: invalid pair '{pair}', expected KEY=VALUE", file=sys.stderr)
            sys.exit(1)
        key, _, value = pair.partition("=")
        pairs[key.strip()] = value.strip()

    path = profile_path(args.profile, base_path=args.dir)
    env = vault.load(str(path), args.passphrase) if path.exists() else {}
    env.update(pairs)
    vault.save(env, str(path), args.passphrase)
    print(f"Set {len(pairs)} key(s) in profile '{args.profile}'.")


def cmd_get(args):
    path = profile_path(args.profile, base_path=args.dir)
    if not path.exists():
        print(f"Error: profile '{args.profile}' not found.", file=sys.stderr)
        sys.exit(1)
    env = vault.load(str(path), args.passphrase)
    if args.key not in env:
        print(f"Error: key '{args.key}' not found.", file=sys.stderr)
        sys.exit(1)
    print(env[args.key])


def cmd_list(args):
    path = profile_path(args.profile, base_path=args.dir)
    if not path.exists():
        print(f"Error: profile '{args.profile}' not found.", file=sys.stderr)
        sys.exit(1)
    env = vault.load(str(path), args.passphrase)
    for key, value in sorted(env.items()):
        print(f"{key}={value}")


def cmd_profiles(args):
    profiles = list_profiles(base_path=args.dir)
    if not profiles:
        print("No profiles found.")
    else:
        for name in profiles:
            print(name)


def cmd_delete_profile(args):
    removed = delete_profile(args.profile, base_path=args.dir)
    if removed:
        print(f"Deleted profile '{args.profile}'.")
    else:
        print(f"Error: profile '{args.profile}' not found.", file=sys.stderr)
        sys.exit(1)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envoy", description="Manage encrypted .env profiles."
    )
    parser.add_argument("-d", "--dir", default=".", help="Base directory")
    parser.add_argument(
        "-p", "--profile", default=DEFAULT_PROFILE, help="Profile name"
    )
    parser.add_argument("--passphrase", required=False, default="secret")

    sub = parser.add_subparsers(dest="command")

    p_set = sub.add_parser("set", help="Set key=value pairs")
    p_set.add_argument("pairs", nargs="+")
    p_set.set_defaults(func=cmd_set)

    p_get = sub.add_parser("get", help="Get a value by key")
    p_get.add_argument("key")
    p_get.set_defaults(func=cmd_get)

    p_list = sub.add_parser("list", help="List all key=value pairs")
    p_list.set_defaults(func=cmd_list)

    p_profiles = sub.add_parser("profiles", help="List all profiles")
    p_profiles.set_defaults(func=cmd_profiles)

    p_del = sub.add_parser("delete-profile", help="Delete a profile vault")
    p_del.set_defaults(func=cmd_delete_profile)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
