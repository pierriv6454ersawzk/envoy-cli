"""Key rotation: re-encrypt a vault profile under a new passphrase."""

from __future__ import annotations

from pathlib import Path

from envoy.vault import load, save
from envoy.profile import profile_path, profile_exists
from envoy.audit import record


def rotate_key(
    profile: str,
    old_passphrase: str,
    new_passphrase: str,
    base_dir: Path | None = None,
) -> None:
    """Load a vault with *old_passphrase* and re-save it with *new_passphrase*.

    Raises
    ------
    FileNotFoundError
        If the profile vault file does not exist.
    ValueError
        If *old_passphrase* is incorrect (propagated from vault.load).
    """
    path = profile_path(profile, base_dir=base_dir)

    if not profile_exists(profile, base_dir=base_dir):
        raise FileNotFoundError(f"Profile '{profile}' not found at {path}")

    data = load(path, old_passphrase)
    save(path, data, new_passphrase)

    record(
        action="rotate_key",
        profile=profile,
        key=None,
        base_dir=base_dir,
    )
