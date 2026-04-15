"""Integration tests for envoy.cli_tag CLI commands."""

from __future__ import annotations

import argparse
import pytest

from envoy.cli_tag import (
    cmd_tag_add,
    cmd_tag_remove,
    cmd_tag_list,
    cmd_tag_find,
    cmd_tag_show_all,
)
from envoy.tag import add_tag


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(**kwargs):
    ns = argparse.Namespace(base_dir=kwargs.pop("base_dir", None), **kwargs)
    return ns


def test_cmd_tag_add_prints_confirmation(base_dir, capsys):
    args = make_args(profile="prod", tag="live", base_dir=base_dir)
    cmd_tag_add(args)
    out = capsys.readouterr().out
    assert "live" in out
    assert "prod" in out


def test_cmd_tag_remove_prints_confirmation(base_dir, capsys):
    add_tag("prod", "live", base_dir=base_dir)
    args = make_args(profile="prod", tag="live", base_dir=base_dir)
    cmd_tag_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_cmd_tag_list_shows_tags(base_dir, capsys):
    add_tag("prod", "live", base_dir=base_dir)
    add_tag("prod", "critical", base_dir=base_dir)
    args = make_args(profile="prod", base_dir=base_dir)
    cmd_tag_list(args)
    out = capsys.readouterr().out
    assert "live" in out
    assert "critical" in out


def test_cmd_tag_list_empty_message(base_dir, capsys):
    args = make_args(profile="ghost", base_dir=base_dir)
    cmd_tag_list(args)
    out = capsys.readouterr().out
    assert "No tags" in out


def test_cmd_tag_find_lists_profiles(base_dir, capsys):
    add_tag("prod", "live", base_dir=base_dir)
    add_tag("staging", "live", base_dir=base_dir)
    args = make_args(tag="live", base_dir=base_dir)
    cmd_tag_find(args)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "staging" in out


def test_cmd_tag_find_no_match_message(base_dir, capsys):
    args = make_args(tag="nope", base_dir=base_dir)
    cmd_tag_find(args)
    out = capsys.readouterr().out
    assert "No profiles" in out


def test_cmd_tag_show_all_empty_message(base_dir, capsys):
    args = make_args(base_dir=base_dir)
    cmd_tag_show_all(args)
    out = capsys.readouterr().out
    assert "No tags" in out


def test_cmd_tag_show_all_lists_mapping(base_dir, capsys):
    add_tag("prod", "live", base_dir=base_dir)
    add_tag("dev", "local", base_dir=base_dir)
    args = make_args(base_dir=base_dir)
    cmd_tag_show_all(args)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "dev" in out
