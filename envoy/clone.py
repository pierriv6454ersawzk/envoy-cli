"""Clone a profile to a new name, optionally within the same base directory."""

from __future__ import annotations

import shutil
from pathlib import Path

from envoy.profile import profile_path, profile_exists, get_vault_dir


class CloneError(Exception):
    pass


def clone_profile(
    source: str,
    destination: str,
    passphrase: str,
    base_dir: str | None = None,
    overwrite: bool = False,
) -> Path:
    """Clone *source* profile vault file to *destination*.

    Parameters
    ----------
    source:      name of the existing profile to copy.
    destination: name of the new profile to create.
    passphrase:  used only to verify the source vault is readable before copy.
    base_dir:    optional override for the vault directory.
    overwrite:   if False (default) raise CloneError when destination exists.

    Returns the Path of the newly created vault file.
    """
    from envoy.vault import load  # local import to avoid cycles

    src_path = profile_path(source, base_dir=base_dir)
    if not src_path.exists():
        raise CloneError(f"Source profile '{source}' does not exist.")

    # Verify passphrase is valid before copying.
    load(src_path, passphrase)

    dst_path = profile_path(destination, base_dir=base_dir)
    if dst_path.exists() and not overwrite:
        raise CloneError(
            f"Destination profile '{destination}' already exists. "
            "Use overwrite=True to replace it."
        )

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dst_path)
    return dst_path
