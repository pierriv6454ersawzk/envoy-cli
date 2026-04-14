"""Profile management for envoy-cli.

Profiles allow users to maintain multiple named environment configurations
(e.g., 'dev', 'staging', 'prod') within a single vault directory.
"""

import os
from pathlib import Path

DEFAULT_PROFILE = "default"
VAULT_DIR = ".envoy"
VAULT_EXTENSION = ".vault"


def get_vault_dir(base_path: str = ".") -> Path:
    """Return the vault directory path, creating it if necessary."""
    vault_dir = Path(base_path) / VAULT_DIR
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir


def profile_path(profile: str = DEFAULT_PROFILE, base_path: str = ".") -> Path:
    """Return the file path for a given profile vault."""
    safe_name = _sanitize_profile_name(profile)
    return get_vault_dir(base_path) / f"{safe_name}{VAULT_EXTENSION}"


def list_profiles(base_path: str = ".") -> list[str]:
    """Return a sorted list of existing profile names."""
    vault_dir = Path(base_path) / VAULT_DIR
    if not vault_dir.exists():
        return []
    profiles = [
        p.stem
        for p in vault_dir.iterdir()
        if p.is_file() and p.suffix == VAULT_EXTENSION
    ]
    return sorted(profiles)


def profile_exists(profile: str = DEFAULT_PROFILE, base_path: str = ".") -> bool:
    """Return True if the given profile vault file exists."""
    return profile_path(profile, base_path).exists()


def delete_profile(profile: str, base_path: str = ".") -> bool:
    """Delete a profile vault. Returns True if deleted, False if not found."""
    path = profile_path(profile, base_path)
    if path.exists():
        path.unlink()
        return True
    return False


def _sanitize_profile_name(name: str) -> str:
    """Ensure profile name is filesystem-safe."""
    if not name or not name.replace("-", "").replace("_", "").isalnum():
        raise ValueError(
            f"Invalid profile name '{name}'. "
            "Use only letters, digits, hyphens, and underscores."
        )
    return name
