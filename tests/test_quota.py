"""Tests for envoy.quota."""

import pytest
from envoy.quota import (
    set_quota, remove_quota, get_quota, list_quotas,
    check_quota, QuotaExceededError, _DEFAULT_LIMIT,
)


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_get_quota_returns_default_when_missing(base_dir):
    assert get_quota("dev", base_dir=base_dir) == _DEFAULT_LIMIT


def test_set_quota_and_get(base_dir):
    set_quota("dev", 10, base_dir=base_dir)
    assert get_quota("dev", base_dir=base_dir) == 10


def test_set_quota_invalid_raises(base_dir):
    with pytest.raises(ValueError):
        set_quota("dev", 0, base_dir=base_dir)


def test_remove_quota_reverts_to_default(base_dir):
    set_quota("dev", 5, base_dir=base_dir)
    remove_quota("dev", base_dir=base_dir)
    assert get_quota("dev", base_dir=base_dir) == _DEFAULT_LIMIT


def test_remove_quota_missing_is_noop(base_dir):
    remove_quota("nonexistent", base_dir=base_dir)  # should not raise


def test_list_quotas_empty(base_dir):
    assert list_quotas(base_dir=base_dir) == {}


def test_list_quotas_shows_set_entries(base_dir):
    set_quota("dev", 20, base_dir=base_dir)
    set_quota("prod", 50, base_dir=base_dir)
    result = list_quotas(base_dir=base_dir)
    assert result == {"dev": 20, "prod": 50}


def test_check_quota_passes_under_limit(base_dir):
    set_quota("dev", 10, base_dir=base_dir)
    check_quota("dev", 9, base_dir=base_dir)  # should not raise


def test_check_quota_raises_when_at_limit(base_dir):
    set_quota("dev", 5, base_dir=base_dir)
    with pytest.raises(QuotaExceededError, match="dev"):
        check_quota("dev", 5, base_dir=base_dir)


def test_check_quota_uses_default_limit(base_dir):
    check_quota("dev", _DEFAULT_LIMIT - 1, base_dir=base_dir)  # should not raise
    with pytest.raises(QuotaExceededError):
        check_quota("dev", _DEFAULT_LIMIT, base_dir=base_dir)
