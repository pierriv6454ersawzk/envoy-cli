"""CLI commands for profile tagging."""

from __future__ import annotations

import argparse
import sys

from envoy.tag import add_tag, remove_tag, list_tags, profiles_with_tag, all_tags


def cmd_tag_add(args: argparse.Namespace) -> None:
    """envoy tag add <profile> <tag>"""
    add_tag(args.profile, args.tag, base_dir=getattr(args, "base_dir", None))
    print(f"Tag '{args.tag}' added to profile '{args.profile}'.")


def cmd_tag_remove(args: argparse.Namespace) -> None:
    """envoy tag remove <profile> <tag>"""
    remove_tag(args.profile, args.tag, base_dir=getattr(args, "base_dir", None))
    print(f"Tag '{args.tag}' removed from profile '{args.profile}'.")


def cmd_tag_list(args: argparse.Namespace) -> None:
    """envoy tag list <profile>"""
    tags = list_tags(args.profile, base_dir=getattr(args, "base_dir", None))
    if not tags:
        print(f"No tags for profile '{args.profile}'.")
    else:
        for t in tags:
            print(t)


def cmd_tag_find(args: argparse.Namespace) -> None:
    """envoy tag find <tag>  — list profiles carrying the tag."""
    profiles = profiles_with_tag(args.tag, base_dir=getattr(args, "base_dir", None))
    if not profiles:
        print(f"No profiles found with tag '{args.tag}'.")
    else:
        for p in profiles:
            print(p)


def cmd_tag_show_all(args: argparse.Namespace) -> None:
    """envoy tag all  — show every profile and its tags."""
    mapping = all_tags(base_dir=getattr(args, "base_dir", None))
    if not mapping:
        print("No tags defined.")
        return
    for profile, tags in sorted(mapping.items()):
        print(f"{profile}: {', '.join(tags)}")


def register_tag_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    tag_parser = subparsers.add_parser("tag", help="Manage profile tags")
    tag_sub = tag_parser.add_subparsers(dest="tag_cmd", required=True)

    p_add = tag_sub.add_parser("add", help="Add a tag to a profile")
    p_add.add_argument("profile")
    p_add.add_argument("tag")
    p_add.set_defaults(func=cmd_tag_add)

    p_rm = tag_sub.add_parser("remove", help="Remove a tag from a profile")
    p_rm.add_argument("profile")
    p_rm.add_argument("tag")
    p_rm.set_defaults(func=cmd_tag_remove)

    p_ls = tag_sub.add_parser("list", help="List tags for a profile")
    p_ls.add_argument("profile")
    p_ls.set_defaults(func=cmd_tag_list)

    p_find = tag_sub.add_parser("find", help="Find profiles with a given tag")
    p_find.add_argument("tag")
    p_find.set_defaults(func=cmd_tag_find)

    p_all = tag_sub.add_parser("all", help="Show all tags")
    p_all.set_defaults(func=cmd_tag_show_all)
