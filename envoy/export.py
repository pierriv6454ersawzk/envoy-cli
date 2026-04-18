"""Export and import .env file utilities for envoy-cli."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from envoy.vault import load, save


def export_env(profile_path: Path, passphrase: str, output_path: Path | None = None) -> str:
    """Export a vault profile to a plaintext .env file string.

    Args:
        profile_path: Path to the encrypted vault file.
        passphrase: Passphrase used to decrypt the vault.
        output_path: Optional file path to write the exported content.

    Returns:
        The plaintext .env content as a string.
    """
    env_vars: Dict[str, str] = load(profile_path, passphrase)

    lines = []
    for key, value in sorted(env_vars.items()):
        # Quote values that contain spaces or special characters
        if any(ch in value for ch in (" ", "\t", "#", "'", '"')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")

    content = "\n".join(lines)
    if lines:
        content += "\n"

    if output_path is not None:
        output_path = Path(output_path)
        output_path.write_text(content, encoding="utf-8")

    return content


def import_env(source_path: Path, profile_path: Path, passphrase: str, overwrite: bool = False) -> Dict[str, str]:
    """Import variables from a plaintext .env file into a vault profile.

    Args:
        source_path: Path to the plaintext .env file to import.
        profile_path: Path to the target encrypted vault file.
        passphrase: Passphrase used to encrypt/decrypt the vault.
        overwrite: If True, existing keys will be overwritten; otherwise they are preserved.

    Returns:
        The merged env vars dict that was saved to the vault.

    Raises:
        FileNotFoundError: If the source .env file does not exist.
        ValueError: If the source file contains no valid key=value entries.
    """
    source_path = Path(source_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    raw = source_path.read_text(encoding="utf-8")
    imported: Dict[str, str] = {}

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if key:
            imported[key] = value

    if not imported:
        raise ValueError(f"No valid key=value entries found in: {source_path}")

    # Merge with existing vault if it exists
    existing: Dict[str, str] = {}
    if Path(profile_path).exists():
        existing = load(profile_path, passphrase)

    if overwrite:
        merged = {**existing, **imported}
    else:
        merged = {**imported, **existing}

    save(profile_path, passphrase, merged)
    return merged
