"""CLI commands for managing notes on profiles and keys."""
from __future__ import annotations
import argparse
import sys
from envoy.note import set_note, get_note, remove_note, list_notes
from envoy.profile import profile_exists


def cmd_note_set(args: argparse.Namespace) -> None:
    if not profile_exists(args.profile, base_dir=args.base_dir):
        print(f"Error: profile '{args.profile}' does not exist.", file=sys.stderr)
        sys.exit(1)
    set_note(args.profile, args.note, key=getattr(args, "key", None), base_dir=args.base_dir)
    target = f"key '{args.key}'" if getattr(args, "key", None) else f"profile '{args.profile}'"
    print(f"Note set for {target}.")


def cmd_note_get(args: argparse.Namespace) -> None:
    note = get_note(args.profile, key=getattr(args, "key", None), base_dir=args.base_dir)
    if note is None:
        target = f"key '{args.key}'" if getattr(args, "key", None) else f"profile '{args.profile}'"
        print(f"No note found for {target}.")
    else:
        print(note)


def cmd_note_remove(args: argparse.Namespace) -> None:
    removed = remove_note(args.profile, key=getattr(args, "key", None), base_dir=args.base_dir)
    target = f"key '{args.key}'" if getattr(args, "key", None) else f"profile '{args.profile}'"
    if removed:
        print(f"Note removed for {target}.")
    else:
        print(f"No note to remove for {target}.")


def cmd_note_list(args: argparse.Namespace) -> None:
    notes = list_notes(args.profile, base_dir=args.base_dir)
    if not notes:
        print(f"No notes for profile '{args.profile}'.")
        return
    for field, text in notes.items():
        label = field.replace("__key__", "key:").replace("__profile__", "profile")
        print(f"  {label}: {text}")


def register_note_commands(subparsers, common_args) -> None:
    p = subparsers.add_parser("note", help="Manage notes on profiles and keys")
    sp = p.add_subparsers(dest="note_cmd", required=True)

    for name, func in [("set", cmd_note_set), ("get", cmd_note_get),
                       ("remove", cmd_note_remove), ("list", cmd_note_list)]:
        sub = sp.add_parser(name)
        common_args(sub)
        sub.add_argument("profile")
        if name in ("set", "get", "remove"):
            sub.add_argument("--key", default=None)
        if name == "set":
            sub.add_argument("note")
        sub.set_defaults(func=func)
