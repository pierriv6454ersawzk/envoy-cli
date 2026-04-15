"""Search for keys or values across profiles."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import List, Optional

from envoy.profile import list_profiles, profile_path
from envoy.vault import load


@dataclass
class SearchResult:
    profile: str
    key: str
    value: str


def search_profiles(
    passphrase: str,
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    profiles: Optional[List[str]] = None,
    base_dir: Optional[str] = None,
) -> List[SearchResult]:
    """Search for matching keys/values across one or more profiles.

    Args:
        passphrase: Decryption passphrase shared across profiles.
        key_pattern:   Glob pattern matched against key names (case-insensitive).
        value_pattern: Glob pattern matched against values (case-sensitive).
        profiles:      Explicit list of profile names to search; defaults to all.
        base_dir:      Override vault base directory (useful in tests).

    Returns:
        List of SearchResult objects for every matching key/value pair.

    Raises:
        ValueError: If neither key_pattern nor value_pattern is provided.
    """
    if key_pattern is None and value_pattern is None:
        raise ValueError("At least one of key_pattern or value_pattern must be given.")

    target_profiles = profiles if profiles is not None else list_profiles(base_dir=base_dir)

    results: List[SearchResult] = []

    for profile in target_profiles:
        path = profile_path(profile, base_dir=base_dir)
        try:
            env = load(path, passphrase)
        except (FileNotFoundError, ValueError):
            # Skip profiles that don't exist or can't be decrypted.
            continue

        for key, value in env.items():
            key_match = (
                key_pattern is None
                or fnmatch.fnmatch(key.upper(), key_pattern.upper())
            )
            value_match = (
                value_pattern is None
                or fnmatch.fnmatch(value, value_pattern)
            )
            if key_match and value_match:
                results.append(SearchResult(profile=profile, key=key, value=value))

    return results
