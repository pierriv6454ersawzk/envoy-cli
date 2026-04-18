"""Tests for envoy.badge"""

import pytest
from envoy.badge import set_badge, remove_badge, get_badge, list_badges, profiles_with_badge, BadgeError
from envoy.vault import save


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile="default"):
    save({"KEY": "val"}, base_dir, profile, "pass")


def test_set_badge_and_get(base_dir):
    _seed(base_dir)
    set_badge(base_dir, "default", "stable")
    assert get_badge(base_dir, "default") == "stable"


def test_get_badge_returns_none_when_missing(base_dir):
    _seed(base_dir)
    assert get_badge(base_dir, "default") is None


def test_set_badge_overwrites_existing(base_dir):
    _seed(base_dir)
    set_badge(base_dir, "default", "draft")
    set_badge(base_dir, "default", "reviewed")
    assert get_badge(base_dir, "default") == "reviewed"


def test_set_badge_invalid_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(BadgeError, match="Invalid badge"):
        set_badge(base_dir, "default", "unknown")


def test_set_badge_missing_profile_raises(base_dir):
    with pytest.raises(BadgeError, match="does not exist"):
        set_badge(base_dir, "ghost", "stable")


def test_remove_badge(base_dir):
    _seed(base_dir)
    set_badge(base_dir, "default", "stable")
    remove_badge(base_dir, "default")
    assert get_badge(base_dir, "default") is None


def test_list_badges(base_dir):
    _seed(base_dir, "dev")
    _seed(base_dir, "prod")
    set_badge(base_dir, "dev", "experimental")
    set_badge(base_dir, "prod", "stable")
    badges = list_badges(base_dir)
    assert badges["dev"] == "experimental"
    assert badges["prod"] == "stable"


def test_profiles_with_badge(base_dir):
    _seed(base_dir, "dev")
    _seed(base_dir, "staging")
    _seed(base_dir, "prod")
    set_badge(base_dir, "dev", "draft")
    set_badge(base_dir, "staging", "draft")
    set_badge(base_dir, "prod", "stable")
    result = profiles_with_badge(base_dir, "draft")
    assert set(result) == {"dev", "staging"}


def test_list_badges_empty(base_dir):
    assert list_badges(base_dir) == {}
