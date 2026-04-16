"""Tests for envoy.expiry module."""

from __future__ import annotations

import time
import pytest
from datetime import datetime, timezone

from envoy import expiry as exp


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_set_key_expiry_returns_datetime(base_dir):
    dt = exp.set_key_expiry(base_dir, "default", "API_KEY", 300)
    assert isinstance(dt, datetime)
    assert dt.tzinfo == timezone.utc


def test_get_key_expiry_returns_none_when_missing(base_dir):
    result = exp.get_key_expiry(base_dir, "default", "MISSING")
    assert result is None


def test_set_and_get_key_expiry(base_dir):
    exp.set_key_expiry(base_dir, "default", "TOKEN", 600)
    dt = exp.get_key_expiry(base_dir, "default", "TOKEN")
    assert dt is not None
    assert dt > datetime.now(timezone.utc)


def test_is_key_expired_false_for_future(base_dir):
    exp.set_key_expiry(base_dir, "default", "K", 9999)
    assert exp.is_key_expired(base_dir, "default", "K") is False


def test_is_key_expired_true_for_past(base_dir):
    exp.set_key_expiry(base_dir, "default", "OLD", 1)
    time.sleep(1.05)
    assert exp.is_key_expired(base_dir, "default", "OLD") is True


def test_is_key_expired_false_when_no_expiry(base_dir):
    assert exp.is_key_expired(base_dir, "default", "NOEXPIRY") is False


def test_remove_key_expiry(base_dir):
    exp.set_key_expiry(base_dir, "default", "X", 100)
    removed = exp.remove_key_expiry(base_dir, "default", "X")
    assert removed is True
    assert exp.get_key_expiry(base_dir, "default", "X") is None


def test_remove_key_expiry_missing_returns_false(base_dir):
    assert exp.remove_key_expiry(base_dir, "default", "GHOST") is False


def test_list_expired_keys(base_dir):
    exp.set_key_expiry(base_dir, "default", "FRESH", 9999)
    exp.set_key_expiry(base_dir, "default", "STALE", 1)
    time.sleep(1.05)
    expired = exp.list_expired_keys(base_dir, "default")
    assert "STALE" in expired
    assert "FRESH" not in expired


def test_list_all_expiries_empty(base_dir):
    result = exp.list_all_expiries(base_dir, "default")
    assert result == {}


def test_set_key_expiry_invalid_seconds_raises(base_dir):
    with pytest.raises(ValueError):
        exp.set_key_expiry(base_dir, "default", "K", 0)


def test_list_all_expiries_returns_datetimes(base_dir):
    exp.set_key_expiry(base_dir, "default", "A", 100)
    exp.set_key_expiry(base_dir, "default", "B", 200)
    result = exp.list_all_expiries(base_dir, "default")
    assert set(result.keys()) == {"A", "B"}
    for dt in result.values():
        assert isinstance(dt, datetime)
