"""Unit tests for envoy.alias."""

from __future__ import annotations

import pytest

from envoy.alias import add_alias, remove_alias, resolve_alias, list_aliases


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def test_add_alias_and_resolve(base_dir):
    add_alias("prod", "production", base_dir=base_dir)
    assert resolve_alias("prod", base_dir=base_dir) == "production"


def test_resolve_missing_alias_returns_none(base_dir):
    assert resolve_alias("nope", base_dir=base_dir) is None


def test_add_alias_overwrites_existing(base_dir):
    add_alias("prod", "production", base_dir=base_dir)
    add_alias("prod", "prod-v2", base_dir=base_dir)
    assert resolve_alias("prod", base_dir=base_dir) == "prod-v2"


def test_list_aliases_empty(base_dir):
    assert list_aliases(base_dir=base_dir) == {}


def test_list_aliases_returns_all(base_dir):
    add_alias("dev", "development", base_dir=base_dir)
    add_alias("stg", "staging", base_dir=base_dir)
    result = list_aliases(base_dir=base_dir)
    assert result == {"dev": "development", "stg": "staging"}


def test_remove_alias(base_dir):
    add_alias("tmp", "temporary", base_dir=base_dir)
    remove_alias("tmp", base_dir=base_dir)
    assert resolve_alias("tmp", base_dir=base_dir) is None


def test_remove_missing_alias_raises(base_dir):
    with pytest.raises(KeyError, match="not found"):
        remove_alias("ghost", base_dir=base_dir)


def test_add_alias_empty_name_raises(base_dir):
    with pytest.raises(ValueError):
        add_alias("", "production", base_dir=base_dir)


def test_add_alias_empty_profile_raises(base_dir):
    with pytest.raises(ValueError):
        add_alias("prod", "", base_dir=base_dir)


def test_multiple_aliases_independent(base_dir):
    add_alias("a", "alpha", base_dir=base_dir)
    add_alias("b", "beta", base_dir=base_dir)
    remove_alias("a", base_dir=base_dir)
    assert resolve_alias("a", base_dir=base_dir) is None
    assert resolve_alias("b", base_dir=base_dir) == "beta"
