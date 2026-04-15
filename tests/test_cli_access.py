"""Unit tests for envoy.cli_access."""

from __future__ import annotations

import argparse
import sys

import pytest

from envoy.access import grant_access, has_access
from envoy.cli_access import (
    cmd_access_check,
    cmd_access_grant,
    cmd_access_list,
    cmd_access_revoke,
    cmd_access_show_all,
)


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(base_dir, **kwargs):
    defaults = {"base_dir": base_dir, "profile": None, "label": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_access_grant_prints_confirmation(base_dir, capsys):
    args = make_args(base_dir, profile="prod", label="alice")
    cmd_access_grant(args)
    out = capsys.readouterr().out
    assert "alice" in out
    assert "prod" in out


def test_cmd_access_grant_missing_profile_exits(base_dir):
    args = make_args(base_dir, profile=None, label="alice")
    with pytest.raises(SystemExit):
        cmd_access_grant(args)


def test_cmd_access_revoke_prints_confirmation(base_dir, capsys):
    grant_access("prod", "alice", base_dir=base_dir)
    args = make_args(base_dir, profile="prod", label="alice")
    cmd_access_revoke(args)
    out = capsys.readouterr().out
    assert "Revoked" in out


def test_cmd_access_list_shows_labels(base_dir, capsys):
    grant_access("prod", "alice", base_dir=base_dir)
    grant_access("prod", "bob", base_dir=base_dir)
    args = make_args(base_dir, profile="prod")
    cmd_access_list(args)
    out = capsys.readouterr().out
    assert "alice" in out
    assert "bob" in out


def test_cmd_access_list_empty(base_dir, capsys):
    args = make_args(base_dir, profile="ghost")
    cmd_access_list(args)
    out = capsys.readouterr().out
    assert "No access" in out


def test_cmd_access_show_all_empty(base_dir, capsys):
    args = make_args(base_dir)
    cmd_access_show_all(args)
    out = capsys.readouterr().out
    assert "No access control" in out


def test_cmd_access_check_passes(base_dir, capsys):
    grant_access("prod", "alice", base_dir=base_dir)
    args = make_args(base_dir, profile="prod", label="alice")
    cmd_access_check(args)  # should not raise
    out = capsys.readouterr().out
    assert "has access" in out


def test_cmd_access_check_fails_exits(base_dir):
    args = make_args(base_dir, profile="prod", label="nobody")
    with pytest.raises(SystemExit) as exc_info:
        cmd_access_check(args)
    assert exc_info.value.code == 2
