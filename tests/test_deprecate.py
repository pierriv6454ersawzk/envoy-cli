"""Tests for envoy.deprecate module."""

import pytest

from envoy.deprecate import (
    DeprecationError,
    deprecate_key,
    get_deprecation,
    is_deprecated,
    list_deprecated_keys,
    undeprecate_key,
)
from envoy.vault import save


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile="default", passphrase="pass"):
    save({"KEY": "value"}, profile, passphrase, base_dir=base_dir)


def test_deprecate_key_creates_entry(base_dir):
    _seed(base_dir)
    deprecate_key("default", "KEY", reason="Use NEW_KEY instead", base_dir=base_dir)
    info = get_deprecation("default", "KEY", base_dir=base_dir)
    assert info is not None
    assert info["reason"] == "Use NEW_KEY instead"


def test_deprecate_key_with_replacement(base_dir):
    _seed(base_dir)
    deprecate_key("default", "KEY", replacement="NEW_KEY", base_dir=base_dir)
    info = get_deprecation("default", "KEY", base_dir=base_dir)
    assert info["replacement"] == "NEW_KEY"


def test_get_deprecation_returns_none_when_missing(base_dir):
    _seed(base_dir)
    result = get_deprecation("default", "MISSING", base_dir=base_dir)
    assert result is None


def test_is_deprecated_true(base_dir):
    _seed(base_dir)
    deprecate_key("default", "KEY", base_dir=base_dir)
    assert is_deprecated("default", "KEY", base_dir=base_dir) is True


def test_is_deprecated_false(base_dir):
    _seed(base_dir)
    assert is_deprecated("default", "KEY", base_dir=base_dir) is False


def test_undeprecate_key_removes_entry(base_dir):
    _seed(base_dir)
    deprecate_key("default", "KEY", base_dir=base_dir)
    undeprecate_key("default", "KEY", base_dir=base_dir)
    assert is_deprecated("default", "KEY", base_dir=base_dir) is False


def test_undeprecate_key_noop_when_missing(base_dir):
    _seed(base_dir)
    # Should not raise
    undeprecate_key("default", "NONEXISTENT", base_dir=base_dir)


def test_list_deprecated_keys_returns_all(base_dir):
    _seed(base_dir, profile="default")
    save({"A": "1", "B": "2", "C": "3"}, "default", "pass", base_dir=base_dir)
    deprecate_key("default", "A", reason="old", base_dir=base_dir)
    deprecate_key("default", "B", replacement="D", base_dir=base_dir)
    result = list_deprecated_keys("default", base_dir=base_dir)
    assert set(result.keys()) == {"A", "B"}


def test_list_deprecated_keys_empty_when_none(base_dir):
    _seed(base_dir)
    result = list_deprecated_keys("default", base_dir=base_dir)
    assert result == {}


def test_deprecate_missing_profile_raises(base_dir):
    with pytest.raises(DeprecationError, match="does not exist"):
        deprecate_key("ghost", "KEY", base_dir=base_dir)


def test_deprecate_key_idempotent(base_dir):
    _seed(base_dir)
    deprecate_key("default", "KEY", reason="first", base_dir=base_dir)
    deprecate_key("default", "KEY", reason="updated", base_dir=base_dir)
    info = get_deprecation("default", "KEY", base_dir=base_dir)
    assert info["reason"] == "updated"
