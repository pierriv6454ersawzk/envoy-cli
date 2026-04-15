"""Tests for envoy/ttl.py — TTL (time-to-live) key expiry."""

import time
import pytest
from pathlib import Path

from envoy.ttl import (
    set_ttl,
    remove_ttl,
    get_ttl,
    is_expired,
    expired_keys,
    purge_expired,
)


@pytest.fixture
def base_dir(tmp_path):
    vault = tmp_path / ".envoy"
    vault.mkdir()
    return str(tmp_path)


def test_set_ttl_stores_expiry(base_dir):
    set_ttl("dev", "API_KEY", 60, base_dir=base_dir)
    expiry = get_ttl("dev", "API_KEY", base_dir=base_dir)
    assert expiry is not None
    assert expiry > time.time()
    assert expiry <= time.time() + 61


def test_get_ttl_returns_none_when_missing(base_dir):
    result = get_ttl("dev", "NONEXISTENT", base_dir=base_dir)
    assert result is None


def test_set_ttl_invalid_seconds_raises(base_dir):
    with pytest.raises(ValueError, match="positive"):
        set_ttl("dev", "KEY", 0, base_dir=base_dir)
    with pytest.raises(ValueError, match="positive"):
        set_ttl("dev", "KEY", -10, base_dir=base_dir)


def test_is_expired_returns_false_for_future_ttl(base_dir):
    set_ttl("dev", "TOKEN", 3600, base_dir=base_dir)
    assert is_expired("dev", "TOKEN", base_dir=base_dir) is False


def test_is_expired_returns_true_for_past_ttl(base_dir):
    set_ttl("dev", "TOKEN", 1, base_dir=base_dir)
    # Manually backdate by writing a past timestamp
    from envoy.ttl import _read_ttl_index, _write_ttl_index
    index = _read_ttl_index("dev", base_dir=base_dir)
    index["TOKEN"] = time.time() - 10
    _write_ttl_index("dev", index, base_dir=base_dir)
    assert is_expired("dev", "TOKEN", base_dir=base_dir) is True


def test_is_expired_returns_false_when_no_ttl_set(base_dir):
    assert is_expired("dev", "NO_TTL_KEY", base_dir=base_dir) is False


def test_remove_ttl_clears_entry(base_dir):
    set_ttl("dev", "SECRET", 120, base_dir=base_dir)
    assert get_ttl("dev", "SECRET", base_dir=base_dir) is not None
    remove_ttl("dev", "SECRET", base_dir=base_dir)
    assert get_ttl("dev", "SECRET", base_dir=base_dir) is None


def test_expired_keys_returns_only_expired(base_dir):
    from envoy.ttl import _read_ttl_index, _write_ttl_index
    now = time.time()
    index = {
        "FRESH_KEY": now + 3600,
        "STALE_KEY": now - 5,
        "ALSO_STALE": now - 1,
    }
    _write_ttl_index("staging", index, base_dir=base_dir)
    result = expired_keys("staging", base_dir=base_dir)
    assert set(result) == {"STALE_KEY", "ALSO_STALE"}


def test_purge_expired_removes_stale_entries(base_dir):
    from envoy.ttl import _read_ttl_index, _write_ttl_index
    now = time.time()
    index = {
        "KEEP": now + 3600,
        "REMOVE_ME": now - 10,
    }
    _write_ttl_index("prod", index, base_dir=base_dir)
    removed = purge_expired("prod", base_dir=base_dir)
    assert removed == ["REMOVE_ME"]
    remaining = _read_ttl_index("prod", base_dir=base_dir)
    assert "KEEP" in remaining
    assert "REMOVE_ME" not in remaining


def test_purge_expired_on_empty_index_returns_empty(base_dir):
    result = purge_expired("empty_profile", base_dir=base_dir)
    assert result == []
