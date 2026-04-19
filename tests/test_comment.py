"""Tests for envoy.comment."""

from __future__ import annotations

import pytest

from envoy.comment import CommentError, get_comment, list_comments, remove_comment, set_comment
from envoy.vault import save


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile="default", passphrase="pass"):
    save({"KEY": "value"}, base_dir, profile, passphrase)


def test_set_and_get_comment(base_dir):
    _seed(base_dir)
    set_comment(base_dir, "default", "KEY", "This is a secret key")
    assert get_comment(base_dir, "default", "KEY") == "This is a secret key"


def test_get_comment_returns_none_when_missing(base_dir):
    _seed(base_dir)
    assert get_comment(base_dir, "default", "MISSING") is None


def test_set_comment_overwrites_existing(base_dir):
    _seed(base_dir)
    set_comment(base_dir, "default", "KEY", "first")
    set_comment(base_dir, "default", "KEY", "second")
    assert get_comment(base_dir, "default", "KEY") == "second"


def test_set_comment_missing_profile_raises(base_dir):
    with pytest.raises(CommentError, match="does not exist"):
        set_comment(base_dir, "ghost", "KEY", "oops")


def test_set_comment_empty_key_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(CommentError, match="empty"):
        set_comment(base_dir, "default", "", "comment")


def test_remove_comment_returns_true(base_dir):
    _seed(base_dir)
    set_comment(base_dir, "default", "KEY", "note")
    assert remove_comment(base_dir, "default", "KEY") is True
    assert get_comment(base_dir, "default", "KEY") is None


def test_remove_comment_returns_false_when_missing(base_dir):
    _seed(base_dir)
    assert remove_comment(base_dir, "default", "NOPE") is False


def test_list_comments_returns_all(base_dir):
    _seed(base_dir)
    set_comment(base_dir, "default", "A", "alpha")
    set_comment(base_dir, "default", "B", "beta")
    result = list_comments(base_dir, "default")
    assert result == {"A": "alpha", "B": "beta"}


def test_list_comments_empty_when_none(base_dir):
    _seed(base_dir)
    assert list_comments(base_dir, "default") == {}
