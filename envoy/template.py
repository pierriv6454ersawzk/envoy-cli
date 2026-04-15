"""Template rendering for .env files — substitute variables from a profile into a template."""

import re
from pathlib import Path
from typing import Optional

from envoy.vault import load

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_template(template_text: str, variables: dict[str, str]) -> str:
    """Replace {{ KEY }} placeholders in *template_text* with values from *variables*.

    Unknown placeholders are left untouched.
    """

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        return variables.get(key, match.group(0))

    return _PLACEHOLDER_RE.sub(_replace, template_text)


def render_template_file(
    template_path: str | Path,
    vault_path: str | Path,
    passphrase: str,
    output_path: Optional[str | Path] = None,
) -> str:
    """Load a vault, read a template file, render it, and optionally write the result.

    Returns the rendered string.
    """
    template_path = Path(template_path)
    vault_path = Path(vault_path)

    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    variables = load(vault_path, passphrase)
    template_text = template_path.read_text(encoding="utf-8")
    rendered = render_template(template_text, variables)

    if output_path is not None:
        Path(output_path).write_text(rendered, encoding="utf-8")

    return rendered


def list_placeholders(template_text: str) -> list[str]:
    """Return a sorted, deduplicated list of placeholder names found in *template_text*."""
    return sorted(set(_PLACEHOLDER_RE.findall(template_text)))
