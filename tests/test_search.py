"""Tests for envoy.search module."""

import pytest

from envoy.profile import profile_path
from envoy.vault import save
from envoy.search import search_profiles, SearchResult


PASS = "hunter2"


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile, data):
    path = profile_path(profile, base_dir=base_dir)
    save(path, data, PASS)


def test_search_by_key_pattern(base_dir):
    _seed(base_dir, "default", {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "prod"})
    results = search_profiles(PASS, key_pattern="DB_*", base_dir=base_dir)
    keys = {r.key for r in results}
    assert keys == {"DB_HOST", "DB_PORT"}


def test_search_by_value_pattern(base_dir):
    _seed(base_dir, "default", {"HOST": "db.example.com", "CACHE": "redis.example.com", "ENV": "prod"})
    results = search_profiles(PASS, value_pattern="*.example.com", base_dir=base_dir)
    keys = {r.key for r in results}
    assert keys == {"HOST", "CACHE"}


def test_search_by_key_and_value(base_dir):
    _seed(base_dir, "default", {"DB_HOST": "db.internal", "DB_PORT": "5432", "APP_HOST": "app.internal"})
    results = search_profiles(PASS, key_pattern="DB_*", value_pattern="*.internal", base_dir=base_dir)
    assert len(results) == 1
    assert results[0].key == "DB_HOST"


def test_search_across_multiple_profiles(base_dir):
    _seed(base_dir, "dev", {"SECRET_KEY": "dev-secret"})
    _seed(base_dir, "prod", {"SECRET_KEY": "prod-secret", "OTHER": "value"})
    results = search_profiles(PASS, key_pattern="SECRET_KEY", base_dir=base_dir)
    profiles_found = {r.profile for r in results}
    assert profiles_found == {"dev", "prod"}


def test_search_limited_to_specific_profiles(base_dir):
    _seed(base_dir, "dev", {"TOKEN": "abc"})
    _seed(base_dir, "prod", {"TOKEN": "xyz"})
    results = search_profiles(PASS, key_pattern="TOKEN", profiles=["dev"], base_dir=base_dir)
    assert len(results) == 1
    assert results[0].profile == "dev"


def test_search_returns_empty_when_no_match(base_dir):
    _seed(base_dir, "default", {"FOO": "bar"})
    results = search_profiles(PASS, key_pattern="NONEXISTENT_*", base_dir=base_dir)
    assert results == []


def test_search_skips_missing_profile(base_dir):
    # "ghost" profile has no vault file — should be silently skipped
    _seed(base_dir, "default", {"KEY": "val"})
    results = search_profiles(PASS, key_pattern="KEY", profiles=["default", "ghost"], base_dir=base_dir)
    assert len(results) == 1
    assert results[0].profile == "default"


def test_search_raises_when_no_pattern_given(base_dir):
    with pytest.raises(ValueError, match="At least one"):
        search_profiles(PASS, base_dir=base_dir)


def test_search_result_contains_value(base_dir):
    _seed(base_dir, "default", {"API_URL": "https://api.example.com"})
    results = search_profiles(PASS, key_pattern="API_URL", base_dir=base_dir)
    assert len(results) == 1
    assert isinstance(results[0], SearchResult)
    assert results[0].value == "https://api.example.com"
