"""Tests for envoy.rotate – key rotation feature."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.vault import save, load
from envoy.rotate import rotate_key
from envoy.profile import profile_path


@pytest.fixture()
def base_dir(tmp_path: Path) -> Path:
    return tmp_path


def _seed_profile(
    base_dir: Path,
    profile: str = "default",
    passphrase: str = "old-secret",
    data: dict | None = None,
) -> Path:
    """Create a vault file and return its path."""
    if data is None:
        data = {"FOO": "bar", "BAZ": "qux"}
    path = profile_path(profile, base_dir=base_dir)
    save(path, data, passphrase)
    return path


def test_rotate_key_allows_new_passphrase(base_dir):
    path = _seed_profile(base_dir)
    rotate_key("default", "old-secret", "new-secret", base_dir=base_dir)
    data = load(path, "new-secret")
    assert data == {"FOO": "bar", "BAZ": "qux"}


def test_rotate_key_old_passphrase_no_longer_works(base_dir):
    _seed_profile(base_dir)
    rotate_key("default", "old-secret", "new-secret", base_dir=base_dir)
    path = profile_path("default", base_dir=base_dir)
    with pytest.raises(ValueError):
        load(path, "old-secret")


def test_rotate_key_wrong_old_passphrase_raises(base_dir):
    _seed_profile(base_dir)
    with pytest.raises(ValueError):
        rotate_key("default", "wrong", "new-secret", base_dir=base_dir)


def test_rotate_key_wrong_old_passphrase_leaves_vault_intact(base_dir):
    """A failed rotation must not corrupt or alter the existing vault."""
    path = _seed_profile(base_dir)
    with pytest.raises(ValueError):
        rotate_key("default", "wrong", "new-secret", base_dir=base_dir)
    # Original passphrase should still unlock the vault unchanged.
    data = load(path, "old-secret")
    assert data == {"FOO": "bar", "BAZ": "qux"}


def test_rotate_key_missing_profile_raises(base_dir):
    with pytest.raises(FileNotFoundError, match="Profile 'ghost' not found"):
        rotate_key("ghost", "old", "new", base_dir=base_dir)


def test_rotate_key_writes_audit_entry(base_dir):
    _seed_profile(base_dir)
    rotate_key("default", "old-secret", "new-secret", base_dir=base_dir)
    from envoy.audit import read_log
    entries = read_log(base_dir=base_dir)
    assert any(e["action"] == "rotate_key" and e["profile"] == "default" for e in entries)
