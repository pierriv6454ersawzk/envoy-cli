"""CLI commands for managing favorite profiles."""

from __future__ import annotations

import sys

from envoy.favorite import add_favorite, remove_favorite, list_favorites, is_favorite


def cmd_favorite_add(args) -> None:
    try:
        add_favorite(args.profile, base_dir=getattr(args, "base_dir", None))
        print(f"✓ '{args.profile}' added to favorites.")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_favorite_remove(args) -> None:
    try:
        remove_favorite(args.profile, base_dir=getattr(args, "base_dir", None))
        print(f"✓ '{args.profile}' removed from favorites.")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_favorite_list(args) -> None:
    favorites = list_favorites(base_dir=getattr(args, "base_dir", None))
    if not favorites:
        print("No favorites set.")
    else:
        for name in favorites:
            print(name)


def cmd_favorite_check(args) -> None:
    result = is_favorite(args.profile, base_dir=getattr(args, "base_dir", None))
    if result:
        print(f"'{args.profile}' is a favorite.")
    else:
        print(f"'{args.profile}' is NOT a favorite.")
        sys.exit(1)


def register_favorite_commands(subparsers) -> None:
    p = subparsers.add_parser("favorite", help="Manage favorite profiles")
    sub = p.add_subparsers(dest="favorite_cmd")

    add_p = sub.add_parser("add", help="Mark a profile as favorite")
    add_p.add_argument("profile")
    add_p.set_defaults(func=cmd_favorite_add)

    rm_p = sub.add_parser("remove", help="Remove a profile from favorites")
    rm_p.add_argument("profile")
    rm_p.set_defaults(func=cmd_favorite_remove)

    list_p = sub.add_parser("list", help="List all favorite profiles")
    list_p.set_defaults(func=cmd_favorite_list)

    check_p = sub.add_parser("check", help="Check if a profile is a favorite")
    check_p.add_argument("profile")
    check_p.set_defaults(func=cmd_favorite_check)
