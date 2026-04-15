"""Copy variables or entire profiles between environments."""

from __future__ import annotations

from typing import Optional

from envoy.vault import load, save
from envoy.profile import profile_path, profile_exists


def copy_keys(
    src_profile: str,
    dst_profile: str,
    src_passphrase: str,
    dst_passphrase: str,
    keys: Optional[list[str]] = None,
    overwrite: bool = True,
    base_dir: Optional[str] = None,
) -> dict[str, str]:
    """Copy specific keys (or all keys) from src_profile into dst_profile.

    Returns a dict of {key: value} pairs that were copied.
    Raises FileNotFoundError if src_profile does not exist.
    Raises KeyError if any of the requested keys are missing in src.
    """
    src_path = profile_path(src_profile, base_dir=base_dir)
    if not profile_exists(src_profile, base_dir=base_dir):
        raise FileNotFoundError(f"Source profile '{src_profile}' does not exist.")

    src_env = load(src_path, src_passphrase)

    if keys is None:
        to_copy = dict(src_env)
    else:
        missing = [k for k in keys if k not in src_env]
        if missing:
            raise KeyError(f"Keys not found in source profile: {missing}")
        to_copy = {k: src_env[k] for k in keys}

    dst_path = profile_path(dst_profile, base_dir=base_dir)
    if profile_exists(dst_profile, base_dir=base_dir):
        dst_env = load(dst_path, dst_passphrase)
    else:
        dst_env = {}

    if overwrite:
        dst_env.update(to_copy)
    else:
        for k, v in to_copy.items():
            if k not in dst_env:
                dst_env[k] = v

    save(dst_path, dst_env, dst_passphrase)
    return to_copy
