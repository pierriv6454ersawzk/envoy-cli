"""Tests for envoy.cli_quota."""

import pytest
from argparse import Namespace
from envoy.cli_quota import cmd_quota_set, cmd_quota_remove, cmd_quota_show, cmd_quota_list
from envoy.quota import set_quota, get_quota, _DEFAULT_LIMIT


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(**kwargs):
    return Namespace(**kwargs)


def test_cmd_quota_set_prints_confirmation(base_dir, capsys):
    args = make_args(profile="dev", limit="15")
    cmd_quota_set(args, base_dir=base_dir)
    out = capsys.readouterr().out
    assert "dev" in out
    assert "15" in out


def test_cmd_quota_set_invalid_limit_exits(base_dir):
    args = make_args(profile="dev", limit="notanumber")
    with pytest.raises(SystemExit):
        cmd_quota_set(args, base_dir=base_dir)


def test_cmd_quota_set_zero_limit_exits(base_dir):
    args = make_args(profile="dev", limit="0")
    with pytest.raises(SystemExit):
        cmd_quota_set(args, base_dir=base_dir)


def test_cmd_quota_remove_prints_confirmation(base_dir, capsys):
    set_quota("dev", 10, base_dir=base_dir)
    args = make_args(profile="dev")
    cmd_quota_remove(args, base_dir=base_dir)
    out = capsys.readouterr().out
    assert "dev" in out
    assert get_quota("dev", base_dir=base_dir) == _DEFAULT_LIMIT


def test_cmd_quota_show_displays_limit(base_dir, capsys):
    set_quota("staging", 25, base_dir=base_dir)
    args = make_args(profile="staging")
    cmd_quota_show(args, base_dir=base_dir)
    out = capsys.readouterr().out
    assert "25" in out


def test_cmd_quota_list_empty(base_dir, capsys):
    args = make_args()
    cmd_quota_list(args, base_dir=base_dir)
    out = capsys.readouterr().out
    assert "No custom quotas" in out


def test_cmd_quota_list_shows_entries(base_dir, capsys):
    set_quota("dev", 10, base_dir=base_dir)
    set_quota("prod", 200, base_dir=base_dir)
    args = make_args()
    cmd_quota_list(args, base_dir=base_dir)
    out = capsys.readouterr().out
    assert "dev" in out
    assert "prod" in out
