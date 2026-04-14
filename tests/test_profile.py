"""Tests for envoy.profile module."""

import pytest
from pathlib import Path
from envoy.profile import (
    profile_path,
    list_profiles,
    profile_exists,
    delete_profile,
    _sanitize_profile_name,
    VAULT_DIR,
    VAULT_EXTENSION,
)


@pytest.fixture
def tmp_base(tmp_path):
    return str(tmp_path)


def test_profile_path_default(tmp_base):
    path = profile_path(base_path=tmp_base)
    assert path.name == f"default{VAULT_EXTENSION}"
    assert VAULT_DIR in str(path)


def test_profile_path_named(tmp_base):
    path = profile_path("staging", base_path=tmp_base)
    assert path.name == f"staging{VAULT_EXTENSION}"


def test_profile_path_creates_vault_dir(tmp_base):
    profile_path(base_path=tmp_base)
    assert (Path(tmp_base) / VAULT_DIR).is_dir()


def test_list_profiles_empty(tmp_base):
    assert list_profiles(tmp_base) == []


def test_list_profiles_returns_sorted(tmp_base):
    for name in ["prod", "dev", "staging"]:
        profile_path(name, base_path=tmp_base).touch()
    assert list_profiles(tmp_base) == ["dev", "prod", "staging"]


def test_profile_exists_false(tmp_base):
    assert not profile_exists("dev", base_path=tmp_base)


def test_profile_exists_true(tmp_base):
    profile_path("dev", base_path=tmp_base).touch()
    assert profile_exists("dev", base_path=tmp_base)


def test_delete_profile_removes_file(tmp_base):
    profile_path("dev", base_path=tmp_base).touch()
    result = delete_profile("dev", base_path=tmp_base)
    assert result is True
    assert not profile_exists("dev", base_path=tmp_base)


def test_delete_profile_returns_false_if_missing(tmp_base):
    assert delete_profile("ghost", base_path=tmp_base) is False


def test_sanitize_profile_name_valid():
    assert _sanitize_profile_name("my-profile_1") == "my-profile_1"


def test_sanitize_profile_name_invalid():
    with pytest.raises(ValueError, match="Invalid profile name"):
        _sanitize_profile_name("bad name!")


def test_sanitize_profile_name_empty():
    with pytest.raises(ValueError):
        _sanitize_profile_name("")
