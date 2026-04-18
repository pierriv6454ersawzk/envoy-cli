"""Profile status summary: key count, TTL, lock, schema, tags."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import os

from envoy.profile import profile_path, profile_exists
from envoy.vault import load
from envoy.ttl import get_ttl, is_profile_expired
from envoy.lock import is_locked, lock_info
from envoy.tag import list_tags
from envoy.schema import load_schema


@dataclass
class ProfileStatus:
    profile: str
    exists: bool
    key_count: int = 0
    is_locked: bool = False
    lock_owner: Optional[str] = None
    ttl_seconds: Optional[int] = None
    is_expired: bool = False
    tags: list = field(default_factory=list)
    schema_keys: int = 0


def get_status(profile: str, passphrase: str, base_dir: Optional[str] = None) -> ProfileStatus:
    """Return a ProfileStatus summary for the given profile."""
    if not profile_exists(profile, base_dir=base_dir):
        return ProfileStatus(profile=profile, exists=False)

    env = load(profile_path(profile, base_dir=base_dir), passphrase)
    locked = is_locked(profile, base_dir=base_dir)
    info = lock_info(profile, base_dir=base_dir) if locked else {}
    ttl = get_ttl(profile, base_dir=base_dir)
    expired = is_profile_expired(profile, base_dir=base_dir)
    tags = list_tags(profile, base_dir=base_dir)
    schema = load_schema(profile, base_dir=base_dir)

    return ProfileStatus(
        profile=profile,
        exists=True,
        key_count=len(env),
        is_locked=locked,
        lock_owner=info.get("pid") if info else None,
        ttl_seconds=ttl,
        is_expired=expired,
        tags=tags,
        schema_keys=len(schema),
    )


def format_status(s: ProfileStatus) -> str:
    """Render a ProfileStatus as a human-readable string."""
    if not s.exists:
        return f"Profile '{s.profile}' does not exist."
    lines = [
        f"Profile : {s.profile}",
        f"Keys    : {s.key_count}",
        f"Locked  : {'yes (pid=' + str(s.lock_owner) + ')' if s.is_locked else 'no'}",
        f"TTL     : {str(s.ttl_seconds) + 's' if s.ttl_seconds is not None else 'none'}",
        f"Expired : {'yes' if s.is_expired else 'no'}",
        f"Tags    : {', '.join(s.tags) if s.tags else 'none'}",
        f"Schema  : {s.schema_keys} rule(s)",
    ]
    return "\n".join(lines)
