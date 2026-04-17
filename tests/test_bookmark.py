"""Tests for envoy.bookmark."""

import pytest

from envoy.bookmark import add_bookmark, remove_bookmark, get_bookmark, list_bookmarks


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_add_bookmark_creates_entry(base_dir):
    add_bookmark("mydb", "production", "DB_URL", base_dir=base_dir)
    bm = get_bookmark("mydb", base_dir=base_dir)
    assert bm is not None
    assert bm["profile"] == "production"
    assert bm["key"] == "DB_URL"


def test_get_bookmark_returns_none_when_missing(base_dir):
    assert get_bookmark("nope", base_dir=base_dir) is None


def test_add_bookmark_overwrites_existing(base_dir):
    add_bookmark("tok", "dev", "API_KEY", base_dir=base_dir)
    add_bookmark("tok", "staging", "API_TOKEN", base_dir=base_dir)
    bm = get_bookmark("tok", base_dir=base_dir)
    assert bm["profile"] == "staging"
    assert bm["key"] == "API_TOKEN"


def test_list_bookmarks_empty(base_dir):
    assert list_bookmarks(base_dir=base_dir) == {}


def test_list_bookmarks_returns_all(base_dir):
    add_bookmark("a", "p1", "K1", base_dir=base_dir)
    add_bookmark("b", "p2", "K2", base_dir=base_dir)
    bms = list_bookmarks(base_dir=base_dir)
    assert len(bms) == 2
    assert "a" in bms
    assert "b" in bms


def test_remove_bookmark(base_dir):
    add_bookmark("x", "prod", "SECRET", base_dir=base_dir)
    remove_bookmark("x", base_dir=base_dir)
    assert get_bookmark("x", base_dir=base_dir) is None


def test_remove_missing_bookmark_raises(base_dir):
    with pytest.raises(KeyError, match="not found"):
        remove_bookmark("ghost", base_dir=base_dir)


def test_add_bookmark_empty_name_raises(base_dir):
    with pytest.raises(ValueError, match="empty"):
        add_bookmark("", "prod", "KEY", base_dir=base_dir)
