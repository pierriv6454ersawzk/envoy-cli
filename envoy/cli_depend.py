"""CLI commands for profile dependency management."""

import sys
from envoy.depend import (
    add_dependency, remove_dependency, get_dependencies,
    get_dependents, list_all, DependencyError
)


def cmd_depend_add(args) -> None:
    try:
        add_dependency(args.base_dir, args.profile, args.depends_on)
        print(f"[depend] '{args.profile}' now depends on '{args.depends_on}'.")
    except DependencyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_depend_remove(args) -> None:
    remove_dependency(args.base_dir, args.profile, args.depends_on)
    print(f"[depend] Removed dependency '{args.depends_on}' from '{args.profile}'.")


def cmd_depend_show(args) -> None:
    deps = get_dependencies(args.base_dir, args.profile)
    if not deps:
        print(f"No dependencies for '{args.profile}'.")
    else:
        print(f"Dependencies of '{args.profile}':")
        for d in deps:
            print(f"  - {d}")


def cmd_depend_reverse(args) -> None:
    dependents = get_dependents(args.base_dir, args.profile)
    if not dependents:
        print(f"No profiles depend on '{args.profile}'.")
    else:
        print(f"Profiles depending on '{args.profile}':")
        for d in dependents:
            print(f"  - {d}")


def cmd_depend_list(args) -> None:
    all_deps = list_all(args.base_dir)
    if not all_deps:
        print("No dependencies defined.")
    else:
        for profile, deps in all_deps.items():
            print(f"{profile}: {', '.join(deps)}")


def register_depend_commands(subparsers, base_dir: str) -> None:
    p = subparsers.add_parser("depend", help="Manage profile dependencies")
    sub = p.add_subparsers(dest="depend_cmd")

    add_p = sub.add_parser("add")
    add_p.add_argument("profile")
    add_p.add_argument("depends_on")
    add_p.set_defaults(func=cmd_depend_add, base_dir=base_dir)

    rm_p = sub.add_parser("remove")
    rm_p.add_argument("profile")
    rm_p.add_argument("depends_on")
    rm_p.set_defaults(func=cmd_depend_remove, base_dir=base_dir)

    show_p = sub.add_parser("show")
    show_p.add_argument("profile")
    show_p.set_defaults(func=cmd_depend_show, base_dir=base_dir)

    rev_p = sub.add_parser("reverse")
    rev_p.add_argument("profile")
    rev_p.set_defaults(func=cmd_depend_reverse, base_dir=base_dir)

    list_p = sub.add_parser("list")
    list_p.set_defaults(func=cmd_depend_list, base_dir=base_dir)
