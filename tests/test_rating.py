"""Tests for envoy.rating module."""

import pytest
from pathlib import Path
from envoy.rating import set_rating, get_rating, remove_rating, list_ratings, RatingError
from envoy.vault import save


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(profile: str, base_dir: str):
    from envoy.profile import profile_path
    path = profile_path(profile, base_dir)
    save({"KEY": "val"}, path, "pass")


def test_set_and_get_rating(base_dir):
    _seed("prod", base_dir)
    set_rating("prod", 4, base_dir)
    assert get_rating("prod", base_dir) == 4


def test_get_rating_returns_none_when_missing(base_dir):
    _seed("prod", base_dir)
    assert get_rating("prod", base_dir) is None


def test_set_rating_overwrites_existing(base_dir):
    _seed("prod", base_dir)
    set_rating("prod", 3, base_dir)
    set_rating("prod", 5, base_dir)
    assert get_rating("prod", base_dir) == 5


def test_set_rating_invalid_score_raises(base_dir):
    _seed("prod", base_dir)
    with pytest.raises(RatingError, match="between"):
        set_rating("prod", 0, base_dir)


def test_set_rating_too_high_raises(base_dir):
    _seed("prod", base_dir)
    with pytest.raises(RatingError, match="between"):
        set_rating("prod", 6, base_dir)


def test_set_rating_missing_profile_raises(base_dir):
    with pytest.raises(RatingError, match="does not exist"):
        set_rating("ghost", 3, base_dir)


def test_remove_rating_returns_true(base_dir):
    _seed("prod", base_dir)
    set_rating("prod", 2, base_dir)
    assert remove_rating("prod", base_dir) is True
    assert get_rating("prod", base_dir) is None


def test_remove_rating_returns_false_when_missing(base_dir):
    _seed("prod", base_dir)
    assert remove_rating("prod", base_dir) is False


def test_list_ratings_empty(base_dir):
    assert list_ratings(base_dir) == {}


def test_list_ratings_multiple(base_dir):
    _seed("prod", base_dir)
    _seed("staging", base_dir)
    set_rating("prod", 5, base_dir)
    set_rating("staging", 3, base_dir)
    result = list_ratings(base_dir)
    assert result == {"prod": 5, "staging": 3}
