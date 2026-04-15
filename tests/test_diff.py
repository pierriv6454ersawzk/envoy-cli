"""Tests for envoy.diff module."""

import pytest

from envoy.diff import DiffEntry, diff_envs, format_diff


LEFT = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "old"}
RIGHT = {"DB_HOST": "localhost", "DB_NAME": "mydb", "SECRET": "new"}


def test_diff_detects_added_key():
    entries = diff_envs(LEFT, RIGHT)
    added = [e for e in entries if e.status == "added"]
    assert len(added) == 1
    assert added[0].key == "DB_NAME"
    assert added[0].right_value == "mydb"


def test_diff_detects_removed_key():
    entries = diff_envs(LEFT, RIGHT)
    removed = [e for e in entries if e.status == "removed"]
    assert len(removed) == 1
    assert removed[0].key == "DB_PORT"
    assert removed[0].left_value == "5432"


def test_diff_detects_changed_key():
    entries = diff_envs(LEFT, RIGHT)
    changed = [e for e in entries if e.status == "changed"]
    assert len(changed) == 1
    assert changed[0].key == "SECRET"
    assert changed[0].left_value == "old"
    assert changed[0].right_value == "new"


def test_diff_hides_unchanged_by_default():
    entries = diff_envs(LEFT, RIGHT)
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert unchanged == []


def test_diff_shows_unchanged_when_requested():
    entries = diff_envs(LEFT, RIGHT, show_unchanged=True)
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert len(unchanged) == 1
    assert unchanged[0].key == "DB_HOST"


def test_diff_identical_envs_returns_empty():
    entries = diff_envs(LEFT, LEFT)
    assert entries == []


def test_format_diff_empty():
    result = format_diff([])
    assert result == "(no differences)"


def test_format_diff_masks_values_by_default():
    entries = diff_envs(LEFT, RIGHT)
    output = format_diff(entries)
    assert "***" in output
    assert "old" not in output
    assert "new" not in output


def test_format_diff_shows_values_when_unmasked():
    entries = diff_envs(LEFT, RIGHT)
    output = format_diff(entries, mask_values=False)
    assert "old" in output
    assert "new" in output
    assert "mydb" in output


def test_format_diff_prefixes():
    entries = diff_envs(LEFT, RIGHT)
    output = format_diff(entries, mask_values=False)
    assert any(line.startswith("  +") for line in output.splitlines())
    assert any(line.startswith("  -") for line in output.splitlines())
    assert any(line.startswith("  ~") for line in output.splitlines())
