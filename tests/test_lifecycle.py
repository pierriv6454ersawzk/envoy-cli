"""Tests for envoy.lifecycle."""

from __future__ import annotations

import pytest

from envoy.lifecycle import (
    LifecycleError,
    all_states,
    get_state,
    list_by_state,
    remove_state,
    set_state,
)
from envoy.vault import save


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir: str, profile: str = "default") -> None:
    save({"KEY": "value"}, profile, "pass", base_dir=base_dir)


def test_get_state_returns_active_by_default(base_dir):
    _seed(base_dir)
    assert get_state("default", base_dir=base_dir) == "active"


def test_set_and_get_state(base_dir):
    _seed(base_dir)
    set_state("default", "inactive", base_dir=base_dir)
    assert get_state("default", base_dir=base_dir) == "inactive"


def test_set_state_overwrites_existing(base_dir):
    _seed(base_dir)
    set_state("default", "inactive", base_dir=base_dir)
    set_state("default", "archived", base_dir=base_dir)
    assert get_state("default", base_dir=base_dir) == "archived"


def test_set_state_invalid_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(LifecycleError, match="Invalid state"):
        set_state("default", "deleted", base_dir=base_dir)


def test_set_state_missing_profile_raises(base_dir):
    with pytest.raises(LifecycleError, match="does not exist"):
        set_state("ghost", "active", base_dir=base_dir)


def test_remove_state_reverts_to_active(base_dir):
    _seed(base_dir)
    set_state("default", "archived", base_dir=base_dir)
    remove_state("default", base_dir=base_dir)
    assert get_state("default", base_dir=base_dir) == "active"


def test_remove_state_missing_profile_is_noop(base_dir):
    remove_state("nonexistent", base_dir=base_dir)  # should not raise


def test_list_by_state_returns_matching_profiles(base_dir):
    _seed(base_dir, "alpha")
    _seed(base_dir, "beta")
    _seed(base_dir, "gamma")
    set_state("alpha", "inactive", base_dir=base_dir)
    set_state("beta", "inactive", base_dir=base_dir)
    set_state("gamma", "archived", base_dir=base_dir)
    result = list_by_state("inactive", base_dir=base_dir)
    assert result == ["alpha", "beta"]


def test_list_by_state_empty_when_none(base_dir):
    _seed(base_dir)
    assert list_by_state("archived", base_dir=base_dir) == []


def test_list_by_state_invalid_raises(base_dir):
    with pytest.raises(LifecycleError, match="Invalid state"):
        list_by_state("unknown", base_dir=base_dir)


def test_all_states_returns_mapping(base_dir):
    _seed(base_dir, "p1")
    _seed(base_dir, "p2")
    set_state("p1", "active", base_dir=base_dir)
    set_state("p2", "archived", base_dir=base_dir)
    states = all_states(base_dir=base_dir)
    assert states["p1"] == "active"
    assert states["p2"] == "archived"


def test_all_states_empty_when_none(base_dir):
    assert all_states(base_dir=base_dir) == {}
