"""Tests for envoy.pin and envoy.cli_pin."""

from __future__ import annotations

import argparse
import sys

import pytest

from envoy.pin import get_pin, list_pins, pin_profile, unpin_profile
from envoy.cli_pin import cmd_pin_set, cmd_pin_remove, cmd_pin_show, cmd_pin_list


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(base_dir, **kwargs):
    ns = argparse.Namespace(base_dir=base_dir, **kwargs)
    return ns


# --- unit tests for pin.py ---

def test_get_pin_returns_none_when_missing(base_dir):
    assert get_pin("default", base_dir=base_dir) is None


def test_pin_profile_and_get_pin(base_dir):
    pin_profile("default", "snap-abc123", base_dir=base_dir)
    assert get_pin("default", base_dir=base_dir) == "snap-abc123"


def test_pin_profile_overwrites_existing(base_dir):
    pin_profile("default", "snap-old", base_dir=base_dir)
    pin_profile("default", "snap-new", base_dir=base_dir)
    assert get_pin("default", base_dir=base_dir) == "snap-new"


def test_unpin_profile_removes_entry(base_dir):
    pin_profile("staging", "snap-xyz", base_dir=base_dir)
    unpin_profile("staging", base_dir=base_dir)
    assert get_pin("staging", base_dir=base_dir) is None


def test_unpin_profile_raises_key_error_when_not_pinned(base_dir):
    with pytest.raises(KeyError, match="not pinned"):
        unpin_profile("nonexistent", base_dir=base_dir)


def test_list_pins_returns_all(base_dir):
    pin_profile("dev", "snap-1", base_dir=base_dir)
    pin_profile("prod", "snap-2", base_dir=base_dir)
    pins = list_pins(base_dir=base_dir)
    assert pins == {"dev": "snap-1", "prod": "snap-2"}


def test_list_pins_empty(base_dir):
    assert list_pins(base_dir=base_dir) == {}


# --- CLI command tests ---

def test_cmd_pin_set_prints_confirmation(base_dir, capsys):
    args = make_args(base_dir, profile="dev", snapshot_id="snap-abc")
    cmd_pin_set(args)
    out = capsys.readouterr().out
    assert "dev" in out and "snap-abc" in out


def test_cmd_pin_remove_success(base_dir, capsys):
    pin_profile("dev", "snap-abc", base_dir=base_dir)
    args = make_args(base_dir, profile="dev")
    cmd_pin_remove(args)
    out = capsys.readouterr().out
    assert "Unpinned" in out


def test_cmd_pin_remove_exits_when_not_pinned(base_dir, capsys):
    args = make_args(base_dir, profile="ghost")
    with pytest.raises(SystemExit) as exc:
        cmd_pin_remove(args)
    assert exc.value.code == 1


def test_cmd_pin_show_displays_snapshot(base_dir, capsys):
    pin_profile("prod", "snap-999", base_dir=base_dir)
    args = make_args(base_dir, profile="prod")
    cmd_pin_show(args)
    out = capsys.readouterr().out
    assert "snap-999" in out


def test_cmd_pin_show_not_pinned_message(base_dir, capsys):
    args = make_args(base_dir, profile="unknown")
    cmd_pin_show(args)
    out = capsys.readouterr().out
    assert "not pinned" in out


def test_cmd_pin_list_shows_all(base_dir, capsys):
    pin_profile("a", "s1", base_dir=base_dir)
    pin_profile("b", "s2", base_dir=base_dir)
    args = make_args(base_dir)
    cmd_pin_list(args)
    out = capsys.readouterr().out
    assert "a" in out and "s1" in out
    assert "b" in out and "s2" in out


def test_cmd_pin_list_empty_message(base_dir, capsys):
    args = make_args(base_dir)
    cmd_pin_list(args)
    out = capsys.readouterr().out
    assert "No profiles" in out
