import time
import pytest
from envoy.history import (
    record_change, get_key_history, clear_key_history, all_keys_with_history
)


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_get_key_history_empty_when_missing(base_dir):
    assert get_key_history("dev", "API_KEY", base_dir=base_dir) == []


def test_record_change_creates_entry(base_dir):
    record_change("dev", "API_KEY", None, "abc123", action="set", base_dir=base_dir)
    entries = get_key_history("dev", "API_KEY", base_dir=base_dir)
    assert len(entries) == 1
    assert entries[0]["action"] == "set"
    assert entries[0]["old"] is None
    assert entries[0]["new"] == "abc123"


def test_record_change_appends_multiple(base_dir):
    record_change("dev", "DB_URL", None, "postgres://a", base_dir=base_dir)
    record_change("dev", "DB_URL", "postgres://a", "postgres://b", base_dir=base_dir)
    entries = get_key_history("dev", "DB_URL", base_dir=base_dir)
    assert len(entries) == 2
    assert entries[1]["old"] == "postgres://a"
    assert entries[1]["new"] == "postgres://b"


def test_record_change_stores_timestamp(base_dir):
    before = time.time()
    record_change("dev", "TOKEN", None, "xyz", base_dir=base_dir)
    after = time.time()
    entry = get_key_history("dev", "TOKEN", base_dir=base_dir)[0]
    assert before <= entry["timestamp"] <= after


def test_all_keys_with_history(base_dir):
    record_change("prod", "KEY_A", None, "1", base_dir=base_dir)
    record_change("prod", "KEY_B", None, "2", base_dir=base_dir)
    keys = all_keys_with_history("prod", base_dir=base_dir)
    assert set(keys) == {"KEY_A", "KEY_B"}


def test_all_keys_empty_when_no_history(base_dir):
    assert all_keys_with_history("staging", base_dir=base_dir) == []


def test_clear_key_history_removes_entries(base_dir):
    record_change("dev", "SECRET", None, "val", base_dir=base_dir)
    result = clear_key_history("dev", "SECRET", base_dir=base_dir)
    assert result is True
    assert get_key_history("dev", "SECRET", base_dir=base_dir) == []


def test_clear_key_history_returns_false_when_missing(base_dir):
    assert clear_key_history("dev", "NONEXISTENT", base_dir=base_dir) is False


def test_history_isolated_per_profile(base_dir):
    record_change("dev", "X", None, "dev_val", base_dir=base_dir)
    assert get_key_history("prod", "X", base_dir=base_dir) == []
