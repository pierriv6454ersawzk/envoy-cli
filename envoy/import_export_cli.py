"""CLI commands for importing and exporting .env files."""

import argparse
import sys
from envoy.export import export_env, import_env
from envoy.profile import profile_path, get_vault_dir
from envoy.audit import record


def cmd_export(args: argparse.Namespace) -> None:
    """Export a profile's env vars to a .env file or stdout."""
    vault_dir = get_vault_dir(args.base_dir)
    path = profile_path(vault_dir, args.profile)

    if not path.exists():
        print(f"[envoy] Profile '{args.profile}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        result = export_env(
            path,
            args.passphrase,
            output_path=args.output,
            mask=args.mask,
        )
    except ValueError as exc:
        print(f"[envoy] Export failed: {exc}", file=sys.stderr)
        sys.exit(1)

    record(vault_dir, args.profile, "export", key=None)

    if args.output:
        print(f"[envoy] Exported to {args.output}")
    else:
        print(result)


def cmd_import(args: argparse.Namespace) -> None:
    """Import key/value pairs from a .env file into a profile."""
    vault_dir = get_vault_dir(args.base_dir)
    path = profile_path(vault_dir, args.profile)

    try:
        count = import_env(
            path,
            args.passphrase,
            args.input,
            overwrite=args.overwrite,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"[envoy] Import failed: {exc}", file=sys.stderr)
        sys.exit(1)

    record(vault_dir, args.profile, "import", key=None)
    print(f"[envoy] Imported {count} variable(s) into profile '{args.profile}'.")


def register_import_export_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    """Register 'export' and 'import' subcommands."""
    # export
    p_export = subparsers.add_parser("export", help="Export env vars to a .env file")
    p_export.add_argument("--profile", default="default", help="Profile name")
    p_export.add_argument("--passphrase", required=True, help="Vault passphrase")
    p_export.add_argument("--output", default=None, help="Output file path (default: stdout)")
    p_export.add_argument("--mask", action="store_true", help="Mask secret values")
    p_export.set_defaults(func=cmd_export)

    # import
    p_import = subparsers.add_parser("import", help="Import env vars from a .env file")
    p_import.add_argument("--profile", default="default", help="Profile name")
    p_import.add_argument("--passphrase", required=True, help="Vault passphrase")
    p_import.add_argument("--input", required=True, help="Input .env file path")
    p_import.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing keys"
    )
    p_import.set_defaults(func=cmd_import)
