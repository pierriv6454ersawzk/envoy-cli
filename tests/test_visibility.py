"""Tests for envoy.visibility."""

from __future__ import annotations

import pytest

from envoy.vault import save
from envoy.visibility import (
    VisibilityError,
    get_visibility,
    list_visibility,
    profiles_with_level,
    remove_visibility,
    set_visibility,
)


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir: str, profile: str = "default") -> None:
    save({"KEY": "val"}, passphrase="pass", base_dir=base_dir, profile=profile)


# ---------------------------------------------------------------------------
# set / get
# ---------------------------------------------------------------------------

def test_get_visibility_returns_private_by_default(base_dir):
    _seed(base_dir)
    assert get_visibility("default", base_dir) == "private"


def test_set_and_get_visibility(base_dir):
    _seed(base_dir)
    set_visibility("default", "public", base_dir)
    assert get_visibility("default", base_dir) == "public"


def test_set_visibility_overwrites_existing(base_dir):
    _seed(base_dir)
    set_visibility("default", "public", base_dir)
    set_visibility("default", "internal", base_dir)
    assert get_visibility("default", base_dir) == "internal"


def test_set_visibility_invalid_level_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(VisibilityError, match="Invalid visibility level"):
        set_visibility("default", "secret", base_dir)


def test_set_visibility_missing_profile_raises(base_dir):
    with pytest.raises(VisibilityError, match="does not exist"):
        set_visibility("ghost", "public", base_dir)


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------

def test_remove_visibility_reverts_to_default(base_dir):
    _seed(base_dir)
    set_visibility("default", "public", base_dir)
    remove_visibility("default", base_dir)
    assert get_visibility("default", base_dir) == "private"


def test_remove_visibility_noop_when_missing(base_dir):
    _seed(base_dir)
    remove_visibility("default", base_dir)  # should not raise


# ---------------------------------------------------------------------------
# list / filter
# ---------------------------------------------------------------------------

def test_list_visibility_empty_when_none_set(base_dir):
    assert list_visibility(base_dir) == {}


def test_list_visibility_returns_all_entries(base_dir):
    _seed(base_dir, "alpha")
    _seed(base_dir, "beta")
    set_visibility("alpha", "public", base_dir)
    set_visibility("beta", "internal", base_dir)
    result = list_visibility(base_dir)
    assert result == {"alpha": "public", "beta": "internal"}


def test_profiles_with_level_returns_matching(base_dir):
    _seed(base_dir, "alpha")
    _seed(base_dir, "beta")
    _seed(base_dir, "gamma")
    set_visibility("alpha", "public", base_dir)
    set_visibility("beta", "public", base_dir)
    set_visibility("gamma", "internal", base_dir)
    assert sorted(profiles_with_level("public", base_dir)) == ["alpha", "beta"]


def test_profiles_with_level_invalid_raises(base_dir):
    with pytest.raises(VisibilityError, match="Invalid visibility level"):
        profiles_with_level("hidden", base_dir)
