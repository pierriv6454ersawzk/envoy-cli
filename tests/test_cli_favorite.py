"""Tests for envoy.cli_favorite."""

from __future__ import annotations

import pytest

from envoy.cli_favorite import (
    cmd_favorite_add,
    cmd_favorite_remove,
    cmd_favorite_list,
    cmd_favorite_check,
)
from envoy.vault import save


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(base_dir, **kwargs):
    class Args:
        pass
    a = Args()
    a.base_dir = base_dir
    for k, v in kwargs.items():
        setattr(a, k, v)
    return a


def _seed(profile, base_dir):
    save({"K": "v"}, profile, "pass", base_dir=base_dir)


def test_cmd_favorite_add_prints_confirmation(base_dir, capsys):
    _seed("dev", base_dir)
    cmd_favorite_add(make_args(base_dir, profile="dev"))
    out = capsys.readouterr().out
    assert "dev" in out and "added" in out


def test_cmd_favorite_add_missing_profile_exits(base_dir):
    with pytest.raises(SystemExit):
        cmd_favorite_add(make_args(base_dir, profile="ghost"))


def test_cmd_favorite_remove_prints_confirmation(base_dir, capsys):
    _seed("dev", base_dir)
    cmd_favorite_add(make_args(base_dir, profile="dev"))
    cmd_favorite_remove(make_args(base_dir, profile="dev"))
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_favorite_remove_not_favorite_exits(base_dir):
    _seed("dev", base_dir)
    with pytest.raises(SystemExit):
        cmd_favorite_remove(make_args(base_dir, profile="dev"))


def test_cmd_favorite_list_empty(base_dir, capsys):
    cmd_favorite_list(make_args(base_dir))
    out = capsys.readouterr().out
    assert "No favorites" in out


def test_cmd_favorite_list_shows_profiles(base_dir, capsys):
    for name in ("dev", "prod"):
        _seed(name, base_dir)
        cmd_favorite_add(make_args(base_dir, profile=name))
    capsys.readouterr()
    cmd_favorite_list(make_args(base_dir))
    out = capsys.readouterr().out
    assert "dev" in out and "prod" in out


def test_cmd_favorite_check_is_favorite(base_dir, capsys):
    _seed("dev", base_dir)
    cmd_favorite_add(make_args(base_dir, profile="dev"))
    capsys.readouterr()
    cmd_favorite_check(make_args(base_dir, profile="dev"))
    out = capsys.readouterr().out
    assert "is a favorite" in out


def test_cmd_favorite_check_not_favorite(base_dir, capsys):
    _seed("dev", base_dir)
    cmd_favorite_check(make_args(base_dir, profile="dev"))
    out = capsys.readouterr().out
    assert "NOT" in out
