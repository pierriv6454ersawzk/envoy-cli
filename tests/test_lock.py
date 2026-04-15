"""Tests for envoy.lock — profile locking."""

import os
import json
import time
import pytest
from pathlib import Path
from unittest.mock import patch

from envoy.lock import acquire_lock, release_lock, is_locked, lock_info, _lock_path


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


# ---------------------------------------------------------------------------
# acquire_lock
# ---------------------------------------------------------------------------

def test_acquire_lock_creates_lock_file(base_dir):
    assert acquire_lock("default", base_dir) is True
    assert _lock_path("default", base_dir).exists()


def test_acquire_lock_returns_false_when_already_locked(base_dir):
    # Seed a fresh lock owned by a *different* PID
    lp = _lock_path("default", base_dir)
    lp.parent.mkdir(parents=True, exist_ok=True)
    lp.write_text(json.dumps({"pid": os.getpid() + 9999, "ts": time.time()}))

    assert acquire_lock("default", base_dir) is False


def test_acquire_lock_overwrites_stale_lock(base_dir):
    lp = _lock_path("default", base_dir)
    lp.parent.mkdir(parents=True, exist_ok=True)
    # Timestamp far in the past → stale
    lp.write_text(json.dumps({"pid": os.getpid() + 9999, "ts": time.time() - 999}))

    assert acquire_lock("default", base_dir) is True


def test_acquire_lock_stores_current_pid(base_dir):
    acquire_lock("prod", base_dir)
    data = json.loads(_lock_path("prod", base_dir).read_text())
    assert data["pid"] == os.getpid()


# ---------------------------------------------------------------------------
# release_lock
# ---------------------------------------------------------------------------

def test_release_lock_removes_file(base_dir):
    acquire_lock("default", base_dir)
    release_lock("default", base_dir)
    assert not _lock_path("default", base_dir).exists()


def test_release_lock_does_not_remove_foreign_lock(base_dir):
    lp = _lock_path("default", base_dir)
    lp.parent.mkdir(parents=True, exist_ok=True)
    lp.write_text(json.dumps({"pid": os.getpid() + 1, "ts": time.time()}))

    release_lock("default", base_dir)
    assert lp.exists()  # should still be there


def test_release_lock_noop_when_no_lock(base_dir):
    # Should not raise
    release_lock("nonexistent", base_dir)


# ---------------------------------------------------------------------------
# is_locked
# ---------------------------------------------------------------------------

def test_is_locked_false_when_no_lock_file(base_dir):
    assert is_locked("default", base_dir) is False


def test_is_locked_false_for_own_lock(base_dir):
    acquire_lock("default", base_dir)
    # Current process owns the lock → not considered "locked" from its perspective
    assert is_locked("default", base_dir) is False


def test_is_locked_true_for_foreign_active_lock(base_dir):
    lp = _lock_path("default", base_dir)
    lp.parent.mkdir(parents=True, exist_ok=True)
    lp.write_text(json.dumps({"pid": os.getpid() + 9999, "ts": time.time()}))
    assert is_locked("default", base_dir) is True


# ---------------------------------------------------------------------------
# lock_info
# ---------------------------------------------------------------------------

def test_lock_info_returns_none_when_missing(base_dir):
    assert lock_info("default", base_dir) is None


def test_lock_info_returns_metadata(base_dir):
    acquire_lock("staging", base_dir)
    info = lock_info("staging", base_dir)
    assert info is not None
    assert info["pid"] == os.getpid()
    assert "ts" in info
