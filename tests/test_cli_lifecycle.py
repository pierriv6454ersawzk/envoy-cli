"""Tests for envoy.cli_lifecycle."""

from __future__ import annotations

import sys
import pytest

from envoy.cli_lifecycle import (
    cmd_lifecycle_all,
    cmd_lifecycle_list,
    cmd_lifecycle_remove,
    cmd_lifecycle_set,
    cmd_lifecycle_show,
)
from envoy.vault import save


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir: str, profile: str = "default") -> None:
    save({"KEY": "val"}, profile, "pass", base_dir=base_dir)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def make_args(**kwargs):
    return Args(**kwargs)


def test_cmd_lifecycle_set_prints_confirmation(base_dir, capsys):
    _seed(base_dir)
    args = make_args(profile="default", state="inactive", base_dir=base_dir)
    cmd_lifecycle_set(args)
    out = capsys.readouterr().out
    assert "inactive" in out
    assert "default" in out


def test_cmd_lifecycle_set_invalid_state_exits(base_dir, capsys):
    _seed(base_dir)
    args = make_args(profile="default", state="broken", base_dir=base_dir)
    with pytest.raises(SystemExit):
        cmd_lifecycle_set(args)
    err = capsys.readouterr().err
    assert "Invalid state" in err


def test_cmd_lifecycle_set_missing_profile_exits(base_dir, capsys):
    args = make_args(profile="ghost", state="active", base_dir=base_dir)
    with pytest.raises(SystemExit):
        cmd_lifecycle_set(args)
    err = capsys.readouterr().err
    assert "does not exist" in err


def test_cmd_lifecycle_show_prints_state(base_dir, capsys):
    _seed(base_dir)
    args = make_args(profile="default", state="archived", base_dir=base_dir)
    cmd_lifecycle_set(args)
    capsys.readouterr()
    show_args = make_args(profile="default", base_dir=base_dir)
    cmd_lifecycle_show(show_args)
    out = capsys.readouterr().out
    assert "archived" in out


def test_cmd_lifecycle_list_shows_profiles(base_dir, capsys):
    _seed(base_dir, "alpha")
    _seed(base_dir, "beta")
    cmd_lifecycle_set(make_args(profile="alpha", state="inactive", base_dir=base_dir))
    cmd_lifecycle_set(make_args(profile="beta", state="inactive", base_dir=base_dir))
    capsys.readouterr()
    cmd_lifecycle_list(make_args(state="inactive", base_dir=base_dir))
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_lifecycle_list_empty_message(base_dir, capsys):
    cmd_lifecycle_list(make_args(state="archived", base_dir=base_dir))
    out = capsys.readouterr().out
    assert "No profiles" in out


def test_cmd_lifecycle_all_shows_all(base_dir, capsys):
    _seed(base_dir, "p1")
    _seed(base_dir, "p2")
    cmd_lifecycle_set(make_args(profile="p1", state="active", base_dir=base_dir))
    cmd_lifecycle_set(make_args(profile="p2", state="archived", base_dir=base_dir))
    capsys.readouterr()
    cmd_lifecycle_all(make_args(base_dir=base_dir))
    out = capsys.readouterr().out
    assert "p1" in out
    assert "p2" in out


def test_cmd_lifecycle_remove_prints_confirmation(base_dir, capsys):
    _seed(base_dir)
    cmd_lifecycle_set(make_args(profile="default", state="inactive", base_dir=base_dir))
    capsys.readouterr()
    cmd_lifecycle_remove(make_args(profile="default", base_dir=base_dir))
    out = capsys.readouterr().out
    assert "removed" in out or "Reverted" in out
