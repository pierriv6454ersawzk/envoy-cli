"""CLI commands for profile badge management."""

import sys
from envoy.badge import set_badge, remove_badge, get_badge, list_badges, profiles_with_badge, BadgeError, VALID_BADGES


def cmd_badge_set(args):
    try:
        set_badge(args.base_dir, args.profile, args.badge)
        print(f"Badge '{args.badge}' set on profile '{args.profile}'.")
    except BadgeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_badge_remove(args):
    remove_badge(args.base_dir, args.profile)
    print(f"Badge removed from profile '{args.profile}'.")


def cmd_badge_show(args):
    badge = get_badge(args.base_dir, args.profile)
    if badge:
        print(f"{args.profile}: {badge}")
    else:
        print(f"No badge set for profile '{args.profile}'.")


def cmd_badge_list(args):
    badges = list_badges(args.base_dir)
    if not badges:
        print("No badges assigned.")
        return
    for profile, badge in sorted(badges.items()):
        print(f"  {profile}: {badge}")


def cmd_badge_find(args):
    profiles = profiles_with_badge(args.base_dir, args.badge)
    if not profiles:
        print(f"No profiles with badge '{args.badge}'.")
        return
    for p in sorted(profiles):
        print(f"  {p}")


def register_badge_commands(subparsers, base_dir):
    p = subparsers.add_parser("badge", help="Manage profile badges")
    sub = p.add_subparsers(dest="badge_cmd")

    s = sub.add_parser("set"); s.add_argument("profile"); s.add_argument("badge", choices=sorted(VALID_BADGES)); s.set_defaults(func=cmd_badge_set, base_dir=base_dir)
    r = sub.add_parser("remove"); r.add_argument("profile"); r.set_defaults(func=cmd_badge_remove, base_dir=base_dir)
    sh = sub.add_parser("show"); sh.add_argument("profile"); sh.set_defaults(func=cmd_badge_show, base_dir=base_dir)
    ls = sub.add_parser("list"); ls.set_defaults(func=cmd_badge_list, base_dir=base_dir)
    f = sub.add_parser("find"); f.add_argument("badge", choices=sorted(VALID_BADGES)); f.set_defaults(func=cmd_badge_find, base_dir=base_dir)
