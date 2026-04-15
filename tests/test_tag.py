"""Unit tests for envoy.tag."""

from __future__ import annotations

import pytest

from envoy.tag import (
    add_tag,
    remove_tag,
    list_tags,
    profiles_with_tag,
    all_tags,
    _tag_index_path,
)


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def test_add_tag_creates_index(base_dir):
    add_tag("prod", "live", base_dir=base_dir)
    assert _tag_index_path(base_dir).exists()


def test_add_tag_appears_in_list(base_dir):
    add_tag("prod", "live", base_dir=base_dir)
    assert "live" in list_tags("prod", base_dir=base_dir)


def test_add_tag_idempotent(base_dir):
    add_tag("prod", "live", base_dir=base_dir)
    add_tag("prod", "live", base_dir=base_dir)
    assert list_tags("prod", base_dir=base_dir).count("live") == 1


def test_add_multiple_tags(base_dir):
    add_tag("prod", "live", base_dir=base_dir)
    add_tag("prod", "critical", base_dir=base_dir)
    tags = list_tags("prod", base_dir=base_dir)
    assert "live" in tags
    assert "critical" in tags


def test_remove_tag(base_dir):
    add_tag("prod", "live", base_dir=base_dir)
    remove_tag("prod", "live", base_dir=base_dir)
    assert "live" not in list_tags("prod", base_dir=base_dir)


def test_remove_tag_cleans_empty_profile(base_dir):
    add_tag("prod", "live", base_dir=base_dir)
    remove_tag("prod", "live", base_dir=base_dir)
    assert "prod" not in all_tags(base_dir=base_dir)


def test_remove_nonexistent_tag_is_noop(base_dir):
    add_tag("prod", "live", base_dir=base_dir)
    remove_tag("prod", "ghost", base_dir=base_dir)  # should not raise
    assert list_tags("prod", base_dir=base_dir) == ["live"]


def test_list_tags_empty_when_missing(base_dir):
    assert list_tags("nonexistent", base_dir=base_dir) == []


def test_profiles_with_tag(base_dir):
    add_tag("prod", "live", base_dir=base_dir)
    add_tag("staging", "live", base_dir=base_dir)
    add_tag("dev", "local", base_dir=base_dir)
    result = profiles_with_tag("live", base_dir=base_dir)
    assert set(result) == {"prod", "staging"}


def test_profiles_with_tag_empty_when_none(base_dir):
    assert profiles_with_tag("nope", base_dir=base_dir) == []


def test_all_tags_returns_full_mapping(base_dir):
    add_tag("prod", "live", base_dir=base_dir)
    add_tag("dev", "local", base_dir=base_dir)
    mapping = all_tags(base_dir=base_dir)
    assert mapping["prod"] == ["live"]
    assert mapping["dev"] == ["local"]
