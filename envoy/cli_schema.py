"""CLI commands for schema management."""

from __future__ import annotations

import json
import sys

from envoy.profile import get_vault_dir, profile_exists
from envoy.schema import load_schema, save_schema, validate_env, VALID_TYPES
from envoy.vault import load as vault_load


def cmd_schema_set(args) -> None:
    """Define or update a schema rule: KEY required=true type=integer."""
    base_dir = get_vault_dir(args.base_dir)
    profile = getattr(args, "profile", "default")

    key = args.key.upper()
    rules: dict = {}

    for pair in args.rules:
        if "=" not in pair:
            print(f"Invalid rule format {pair!r}. Use name=value.", file=sys.stderr)
            sys.exit(1)
        rname, rval = pair.split("=", 1)
        if rname == "required":
            rules["required"] = rval.lower() in {"true", "1", "yes"}
        elif rname == "type":
            if rval not in VALID_TYPES:
                print(
                    f"Unknown type {rval!r}. Valid: {', '.join(sorted(VALID_TYPES))}",
                    file=sys.stderr,
                )
                sys.exit(1)
            rules["type"] = rval
        elif rname == "description":
            rules["description"] = rval
        else:
            print(f"Unknown rule {rname!r}.", file=sys.stderr)
            sys.exit(1)

    schema = load_schema(base_dir, profile)
    schema[key] = rules
    save_schema(base_dir, profile, schema)
    print(f"Schema rule set for {key} in profile '{profile}'.")


def cmd_schema_show(args) -> None:
    """Display the schema for a profile."""
    base_dir = get_vault_dir(args.base_dir)
    profile = getattr(args, "profile", "default")
    schema = load_schema(base_dir, profile)
    if not schema:
        print(f"No schema defined for profile '{profile}'.")
        return
    print(json.dumps(schema, indent=2))


def cmd_schema_validate(args) -> None:
    """Validate the current vault against its schema."""
    base_dir = get_vault_dir(args.base_dir)
    profile = getattr(args, "profile", "default")

    if not profile_exists(base_dir, profile):
        print(f"Profile '{profile}' does not exist.", file=sys.stderr)
        sys.exit(1)

    schema = load_schema(base_dir, profile)
    if not schema:
        print(f"No schema defined for profile '{profile}'. Nothing to validate.")
        return

    env = vault_load(base_dir, profile, args.passphrase)
    violations = validate_env(env, schema)

    if not violations:
        print(f"Profile '{profile}' is valid against its schema.")
        return

    for v in violations:
        print(str(v))
    errors = [v for v in violations if v.severity == "error"]
    if errors:
        sys.exit(1)


def register_schema_commands(subparsers, common_args) -> None:
    sp = subparsers.add_parser("schema", help="Manage profile schemas")
    ss = sp.add_subparsers(dest="schema_cmd")

    p_set = ss.add_parser("set", help="Set a schema rule for a key")
    common_args(p_set)
    p_set.add_argument("key")
    p_set.add_argument("rules", nargs="+", metavar="name=value")
    p_set.set_defaults(func=cmd_schema_set)

    p_show = ss.add_parser("show", help="Show schema for a profile")
    common_args(p_show)
    p_show.set_defaults(func=cmd_schema_show)

    p_val = ss.add_parser("validate", help="Validate vault against schema")
    common_args(p_val)
    p_val.add_argument("--passphrase", required=True)
    p_val.set_defaults(func=cmd_schema_validate)
