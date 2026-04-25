"""CLI commands for profile endorsements."""

from __future__ import annotations

import sys
from typing import Optional

from envoy.endorsement import (
    EndorsementError,
    all_endorsements,
    endorse_profile,
    is_endorsed_by,
    list_endorsements,
    revoke_endorsement,
)


def cmd_endorse_add(args) -> None:
    try:
        entry = endorse_profile(
            args.profile,
            args.reviewer,
            note=getattr(args, "note", "") or "",
            base_dir=getattr(args, "base_dir", None),
        )
    except EndorsementError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Endorsed '{args.profile}' by '{entry['reviewer']}'.")


def cmd_endorse_revoke(args) -> None:
    removed = revoke_endorsement(
        args.profile,
        args.reviewer,
        base_dir=getattr(args, "base_dir", None),
    )
    if removed:
        print(f"Revoked endorsement of '{args.profile}' by '{args.reviewer}'.")
    else:
        print(f"No endorsement found for '{args.profile}' by '{args.reviewer}'.")


def cmd_endorse_list(args) -> None:
    entries = list_endorsements(
        args.profile,
        base_dir=getattr(args, "base_dir", None),
    )
    if not entries:
        print(f"No endorsements for profile '{args.profile}'.")
        return
    for e in entries:
        note_part = f" — {e['note']}" if e.get("note") else ""
        print(f"  {e['reviewer']}{note_part}")


def cmd_endorse_check(args) -> None:
    result = is_endorsed_by(
        args.profile,
        args.reviewer,
        base_dir=getattr(args, "base_dir", None),
    )
    if result:
        print(f"'{args.profile}' IS endorsed by '{args.reviewer}'.")
    else:
        print(f"'{args.profile}' is NOT endorsed by '{args.reviewer}'.")


def cmd_endorse_all(args) -> None:
    index = all_endorsements(base_dir=getattr(args, "base_dir", None))
    if not index:
        print("No endorsements recorded.")
        return
    for profile, entries in sorted(index.items()):
        reviewers = ", ".join(e["reviewer"] for e in entries)
        print(f"  {profile}: {reviewers}")


def register_endorsement_commands(subparsers) -> None:
    p = subparsers.add_parser("endorse-add", help="Endorse a profile")
    p.add_argument("profile")
    p.add_argument("reviewer")
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_endorse_add)

    p = subparsers.add_parser("endorse-revoke", help="Revoke an endorsement")
    p.add_argument("profile")
    p.add_argument("reviewer")
    p.set_defaults(func=cmd_endorse_revoke)

    p = subparsers.add_parser("endorse-list", help="List endorsements for a profile")
    p.add_argument("profile")
    p.set_defaults(func=cmd_endorse_list)

    p = subparsers.add_parser("endorse-check", help="Check if a profile is endorsed by reviewer")
    p.add_argument("profile")
    p.add_argument("reviewer")
    p.set_defaults(func=cmd_endorse_check)

    p = subparsers.add_parser("endorse-all", help="Show all endorsements")
    p.set_defaults(func=cmd_endorse_all)
