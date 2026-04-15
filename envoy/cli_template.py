"""CLI commands for template rendering."""

import argparse
import sys
from pathlib import Path

from envoy.profile import profile_path
from envoy.template import list_placeholders, render_template_file


def cmd_template_render(args: argparse.Namespace) -> None:
    """Render a template file using secrets from a vault profile."""
    vault = profile_path(args.profile, base_dir=getattr(args, "base_dir", None))

    if not vault.exists():
        print(f"[error] profile '{args.profile}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        rendered = render_template_file(
            template_path=args.template,
            vault_path=vault,
            passphrase=args.passphrase,
            output_path=getattr(args, "output", None),
        )
    except FileNotFoundError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"[error] decryption failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if not getattr(args, "output", None):
        print(rendered, end="")
    else:
        print(f"[ok] rendered template written to {args.output}")


def cmd_template_inspect(args: argparse.Namespace) -> None:
    """List all {{ PLACEHOLDER }} variables found in a template file."""
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"[error] template file not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    text = template_path.read_text(encoding="utf-8")
    placeholders = list_placeholders(text)

    if not placeholders:
        print("No placeholders found.")
    else:
        print(f"Placeholders in {template_path.name}:")
        for name in placeholders:
            print(f"  {name}")


def register_template_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # render
    p_render = subparsers.add_parser("template-render", help="Render a template using a vault profile")
    p_render.add_argument("template", help="Path to the template file")
    p_render.add_argument("--profile", default="default", help="Profile name")
    p_render.add_argument("--passphrase", required=True, help="Vault passphrase")
    p_render.add_argument("--output", default=None, help="Write rendered output to this file")
    p_render.set_defaults(func=cmd_template_render)

    # inspect
    p_inspect = subparsers.add_parser("template-inspect", help="List placeholders in a template file")
    p_inspect.add_argument("template", help="Path to the template file")
    p_inspect.set_defaults(func=cmd_template_inspect)
