"""CLI commands for managing per-key comments."""

from __future__ import annotations

import sys

from envoy.comment import CommentError, get_comment, list_comments, remove_comment, set_comment


def cmd_comment_set(args) -> None:
    try:
        set_comment(args.base_dir, args.profile, args.key, args.comment)
        print(f"Comment set for '{args.key}' in profile '{args.profile}'.")
    except CommentError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_comment_get(args) -> None:
    comment = get_comment(args.base_dir, args.profile, args.key)
    if comment is None:
        print(f"No comment found for '{args.key}'.")
    else:
        print(comment)


def cmd_comment_remove(args) -> None:
    removed = remove_comment(args.base_dir, args.profile, args.key)
    if removed:
        print(f"Comment removed for '{args.key}' in profile '{args.profile}'.")
    else:
        print(f"No comment found for '{args.key}'.")


def cmd_comment_list(args) -> None:
    comments = list_comments(args.base_dir, args.profile)
    if not comments:
        print(f"No comments for profile '{args.profile}'.")
        return
    for key, comment in sorted(comments.items()):
        print(f"  {key}: {comment}")


def register_comment_commands(subparsers, base_dir: str) -> None:
    p = subparsers.add_parser("comment", help="Manage per-key comments")
    sub = p.add_subparsers(dest="comment_cmd", required=True)

    ps = sub.add_parser("set", help="Set a comment for a key")
    ps.add_argument("profile")
    ps.add_argument("key")
    ps.add_argument("comment")
    ps.set_defaults(func=cmd_comment_set, base_dir=base_dir)

    pg = sub.add_parser("get", help="Get the comment for a key")
    pg.add_argument("profile")
    pg.add_argument("key")
    pg.set_defaults(func=cmd_comment_get, base_dir=base_dir)

    pr = sub.add_parser("remove", help="Remove the comment for a key")
    pr.add_argument("profile")
    pr.add_argument("key")
    pr.set_defaults(func=cmd_comment_remove, base_dir=base_dir)

    pl = sub.add_parser("list", help="List all comments for a profile")
    pl.add_argument("profile")
    pl.set_defaults(func=cmd_comment_list, base_dir=base_dir)
