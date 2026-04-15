"""Key rename operations across a single profile vault."""

from __future__ import annotations

from envoy.vault import load, save
from envoy.audit import record


class RenameError(Exception):
    """Raised when a rename operation cannot be completed."""


def rename_key(
    profile: str,
    old_key: str,
    new_key: str,
    passphrase: str,
    *,
    base_dir: str | None = None,
    overwrite: bool = False,
) -> dict[str, str]:
    """Rename *old_key* to *new_key* inside *profile*.

    Returns the updated env mapping.

    Raises
    ------
    RenameError
        If *old_key* does not exist, *new_key* already exists and
        *overwrite* is False, or *old_key* == *new_key*.
    """
    if old_key == new_key:
        raise RenameError(f"Old and new key are identical: '{old_key}'")

    env = load(profile, passphrase, base_dir=base_dir)

    if old_key not in env:
        raise RenameError(f"Key '{old_key}' not found in profile '{profile}'")

    if new_key in env and not overwrite:
        raise RenameError(
            f"Key '{new_key}' already exists in profile '{profile}'. "
            "Pass overwrite=True to replace it."
        )

    value = env.pop(old_key)
    env[new_key] = value

    save(profile, env, passphrase, base_dir=base_dir)

    record(profile, "rename", old_key, base_dir=base_dir)
    record(profile, "rename", new_key, base_dir=base_dir)

    return env
