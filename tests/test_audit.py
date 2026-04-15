"""Tests for envoy.audit module."""

import pytest
from pathlib import Path
from envoy.audit import record, read_log, clear_log


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_record_creates_log_file(base_dir):
    record("set", "default", key="API_KEY", base_dir=base_dir)
    log_file = Path(base_dir) / "audit.log"
    assert log_file.exists()


def test_read_log_returns_empty_when_missing(base_dir):
    entries = read_log(base_dir=base_dir)
    assert entries == []


def test_record_and_read_single_entry(base_dir):
    record("set", "default", key="DB_URL", base_dir=base_dir)
    entries = read_log(base_dir=base_dir)
    assert len(entries) == 1
    assert entries[0]["action"] == "set"
    assert entries[0]["profile"] == "default"
    assert entries[0]["key"] == "DB_URL"
    assert "timestamp" in entries[0]


def test_record_without_key(base_dir):
    record("load", "production", base_dir=base_dir)
    entries = read_log(base_dir=base_dir)
    assert len(entries) == 1
    assert "key" not in entries[0]


def test_record_multiple_entries(base_dir):
    record("set", "default", key="FOO", base_dir=base_dir)
    record("get", "default", key="FOO", base_dir=base_dir)
    record("delete", "default", key="FOO", base_dir=base_dir)
    entries = read_log(base_dir=base_dir)
    assert len(entries) == 3
    assert [e["action"] for e in entries] == ["set", "get", "delete"]


def test_clear_log_removes_file(base_dir):
    record("set", "default", key="X", base_dir=base_dir)
    clear_log(base_dir=base_dir)
    assert read_log(base_dir=base_dir) == []


def test_clear_log_no_error_when_missing(base_dir):
    # Should not raise even if log does not exist
    clear_log(base_dir=base_dir)
