"""Tests for envoy.clone."""

import pytest
from pathlib import Path

from envoy.clone import clone_profile, CloneError
from envoy.vault import save, load
from envoy.profile import profile_path


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(name: str, data: dict, passphrase: str, base_dir: str) -> Path:
    path = profile_path(name, base_dir=base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    save(path, data, passphrase)
    return path


def test_clone_creates_destination(base_dir):
    _seed("prod", {"KEY": "val"}, "secret", base_dir)
    dst = clone_profile("prod", "staging", "secret", base_dir=base_dir)
    assert dst.exists()


def test_clone_destination_readable_with_same_passphrase(base_dir):
    _seed("prod", {"KEY": "hello"}, "secret", base_dir)
    dst = clone_profile("prod", "staging", "secret", base_dir=base_dir)
    data = load(dst, "secret")
    assert data["KEY"] == "hello"


def test_clone_missing_source_raises(base_dir):
    with pytest.raises(CloneError, match="does not exist"):
        clone_profile("ghost", "copy", "secret", base_dir=base_dir)


def test_clone_wrong_passphrase_raises(base_dir):
    _seed("prod", {"K": "v"}, "correct", base_dir)
    with pytest.raises(ValueError):
        clone_profile("prod", "staging", "wrong", base_dir=base_dir)


def test_clone_existing_destination_raises_by_default(base_dir):
    _seed("prod", {"K": "v"}, "secret", base_dir)
    _seed("staging", {"K": "old"}, "secret", base_dir)
    with pytest.raises(CloneError, match="already exists"):
        clone_profile("prod", "staging", "secret", base_dir=base_dir)


def test_clone_overwrite_replaces_destination(base_dir):
    _seed("prod", {"K": "new"}, "secret", base_dir)
    _seed("staging", {"K": "old"}, "secret", base_dir)
    dst = clone_profile("prod", "staging", "secret", base_dir=base_dir, overwrite=True)
    data = load(dst, "secret")
    assert data["K"] == "new"


def test_clone_preserves_all_keys(base_dir):
    original = {"A": "1", "B": "2", "C": "3"}
    _seed("prod", original, "pass", base_dir)
    dst = clone_profile("prod", "dev", "pass", base_dir=base_dir)
    assert load(dst, "pass") == original
