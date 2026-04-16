"""Merge keys from one or more source profiles into a target profile."""
from typing import Optional
from envoy.vault import load, save
from envoy.profile import profile_path, profile_exists


class MergeError(Exception):
    pass


def merge_profiles(
    sources: list[str],
    target: str,
    passphrase: str,
    base_dir: Optional[str] = None,
    overwrite: bool = True,
) -> dict[str, int]:
    """Merge keys from source profiles into target profile.

    Args:
        sources: List of source profile names.
        target: Target profile name.
        passphrase: Shared passphrase used for all vaults.
        base_dir: Optional base directory override.
        overwrite: If True, source keys overwrite existing target keys.

    Returns:
        Dict mapping source profile name to number of keys merged.
    """
    if not profile_exists(target, base_dir):
        raise MergeError(f"Target profile '{target}' does not exist.")

    target_path = profile_path(target, base_dir)
    target_env = load(str(target_path), passphrase)

    stats: dict[str, int] = {}

    for source in sources:
        if not profile_exists(source, base_dir):
            raise MergeError(f"Source profile '{source}' does not exist.")
        if source == target:
            raise MergeError("Source and target profile must differ.")

        source_path = profile_path(source, base_dir)
        source_env = load(str(source_path), passphrase)

        count = 0
        for key, value in source_env.items():
            if overwrite or key not in target_env:
                target_env[key] = value
                count += 1
        stats[source] = count

    save(str(target_path), target_env, passphrase)
    return stats
