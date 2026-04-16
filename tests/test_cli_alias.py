"""Integration tests for envoy.cli_alias CLI commands."""

from __future__ import annotations

import argparse
import pytest

from envoy.alias import add_alias
from envoy.cli_alias import (
    cmd_alias_add,
    cmd_alias_remove,
    cmd_alias_show,
    cmd_alias_list,
)


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(base_dir, **kwargs):
    ns = argparse.Namespace(base_dir=base_dir, **kwargs)
    return ns


def test_cmd_alias_add_prints_confirmation(base_dir, capsys):
    cmd_alias_add(make_args(base_dir, alias="prod", profile="production"))
    out = capsys.readouterr().out
    assert "prod" in out
    assert "production" in out


def test_cmd_alias_add_empty_alias_exits(base_dir):
    with pytest.raises(SystemExit):
        cmd_alias_add(make_args(base_dir, alias="", profile="production"))


def test_cmd_alias_add_duplicate_exits(base_dir):
    add_alias("prod", "production", base_dir=base_dir)
    with pytest.raises(SystemExit):
        cmd_alias_add(make_args(base_dir, alias="prod", profile="other"))


def test_cmd_alias_remove_prints_confirmation(base_dir, capsys):
    add_alias("dev", "development", base_dir=base_dir)
    cmd_alias_remove(make_args(base_dir, alias="dev"))
    out = capsys.readouterr().out
    assert "dev" in out


def test_cmd_alias_remove_missing_exits(base_dir):
    with pytest.raises(SystemExit):
        cmd_alias_remove(make_args(base_dir, alias="ghost"))


def test_cmd_alias_show_prints_profile(base_dir, capsys):
    add_alias("stg", "staging", base_dir=base_dir)
    cmd_alias_show(make_args(base_dir, alias="stg"))
    out = capsys.readouterr().out
    assert "staging" in out


def test_cmd_alias_show_missing_exits(base_dir):
    with pytest.raises(SystemExit):
        cmd_alias_show(make_args(base_dir, alias="missing"))


def test_cmd_alias_list_empty(base_dir, capsys):
    cmd_alias_list(make_args(base_dir))
    out = capsys.readouterr().out
    assert "No aliases" in out


def test_cmd_alias_list_shows_all(base_dir, capsys):
    add_alias("dev", "development", base_dir=base_dir)
    add_alias("prod", "production", base_dir=base_dir)
    cmd_alias_list(make_args(base_dir))
    out = capsys.readouterr().out
    assert "dev" in out
    assert "development" in out
    assert "prod" in out
    assert "production" in out
