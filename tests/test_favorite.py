"""Tests for envoy.favorite."""

from __future__ import annotations

import pytest

from envoy.favorite import add_favorite, remove_favorite, list_favorites, is_favorite
from envoy.vault import save


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(profile: str, base_dir: str) -> None:
    save({"KEY": "value"}, profile, "pass", base_dir=base_dir)


def test_add_favorite_creates_entry(base_dir):
    _seed("dev", base_dir)
    add_favorite("dev", base_dir=base_dir)
    assert "dev" in list_favorites(base_dir=base_dir)


def test_add_favorite_idempotent(base_dir):
    _seed("dev", base_dir)
    add_favorite("dev", base_dir=base_dir)
    add_favorite("dev", base_dir=base_dir)
    assert list_favorites(base_dir=base_dir).count("dev") == 1


def test_add_favorite_missing_profile_raises(base_dir):
    with pytest.raises(ValueError, match="does not exist"):
        add_favorite("ghost", base_dir=base_dir)


def test_remove_favorite(base_dir):
    _seed("dev", base_dir)
    add_favorite("dev", base_dir=base_dir)
    remove_favorite("dev", base_dir=base_dir)
    assert "dev" not in list_favorites(base_dir=base_dir)


def test_remove_favorite_not_in_list_raises(base_dir):
    _seed("dev", base_dir)
    with pytest.raises(ValueError, match="not a favorite"):
        remove_favorite("dev", base_dir=base_dir)


def test_list_favorites_empty_when_none(base_dir):
    assert list_favorites(base_dir=base_dir) == []


def test_list_favorites_multiple(base_dir):
    for name in ("dev", "staging", "prod"):
        _seed(name, base_dir)
        add_favorite(name, base_dir=base_dir)
    result = list_favorites(base_dir=base_dir)
    assert result == ["dev", "staging", "prod"]


def test_is_favorite_true(base_dir):
    _seed("dev", base_dir)
    add_favorite("dev", base_dir=base_dir)
    assert is_favorite("dev", base_dir=base_dir) is True


def test_is_favorite_false(base_dir):
    _seed("dev", base_dir)
    assert is_favorite("dev", base_dir=base_dir) is False
