"""Tests for envoy.watch – VaultWatcher file-change detection."""

from __future__ import annotations

import os
import time
import threading

import pytest

from envoy.watch import VaultWatcher, watch_profile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _touch(path: str) -> None:
    """Update the mtime of *path* (creates the file if needed)."""
    with open(path, "ab"):
        os.utime(path, None)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_watcher_detects_change(tmp_path):
    vault = tmp_path / "dev.vault"
    _touch(str(vault))

    events: list[str] = []
    watcher = VaultWatcher(str(vault), lambda p: events.append(p), interval=0.05)
    watcher.start()

    time.sleep(0.08)
    _touch(str(vault))          # trigger a change
    time.sleep(0.15)
    watcher.stop()

    assert len(events) >= 1
    assert events[0] == str(vault)


def test_watcher_no_false_positives(tmp_path):
    vault = tmp_path / "prod.vault"
    _touch(str(vault))

    events: list[str] = []
    watcher = VaultWatcher(str(vault), lambda p: events.append(p), interval=0.05)
    watcher.start()
    time.sleep(0.20)            # no changes during this window
    watcher.stop()

    assert events == []


def test_watcher_handles_missing_file(tmp_path):
    vault = tmp_path / "missing.vault"  # does NOT exist
    fired = threading.Event()
    watcher = VaultWatcher(str(vault), lambda p: fired.set(), interval=0.05)
    watcher.start()
    time.sleep(0.08)
    _touch(str(vault))          # file appears → change detected
    fired.wait(timeout=0.30)
    watcher.stop()

    assert fired.is_set()


def test_watcher_is_alive_and_stop(tmp_path):
    vault = tmp_path / "alive.vault"
    _touch(str(vault))

    watcher = VaultWatcher(str(vault), lambda p: None, interval=0.05)
    assert not watcher.is_alive()
    watcher.start()
    assert watcher.is_alive()
    watcher.stop()
    assert not watcher.is_alive()


def test_watch_profile_convenience(tmp_path):
    vault = tmp_path / "staging.vault"
    _touch(str(vault))

    events: list[str] = []
    watcher = watch_profile(str(vault), lambda p: events.append(p), interval=0.05)
    assert watcher.is_alive()

    time.sleep(0.08)
    _touch(str(vault))
    time.sleep(0.15)
    watcher.stop()

    assert len(events) >= 1


def test_callback_exception_does_not_crash_watcher(tmp_path):
    vault = tmp_path / "err.vault"
    _touch(str(vault))

    def bad_callback(p: str) -> None:
        raise RuntimeError("boom")

    watcher = VaultWatcher(str(vault), bad_callback, interval=0.05)
    watcher.start()
    time.sleep(0.08)
    _touch(str(vault))
    time.sleep(0.15)            # watcher should still be alive after exception
    assert watcher.is_alive()
    watcher.stop()
