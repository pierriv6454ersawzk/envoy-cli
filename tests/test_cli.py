"""Tests for envoy CLI — including profile-aware commands."""

import pytest
from unittest.mock import patch
from envoy.cli import build_parser, cmd_set, cmd_get, cmd_list, cmd_profiles, cmd_delete_profile
from envoy.profile import profile_path


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(base_dir, command, profile="default", passphrase="secret", **kwargs):
    parser = build_parser()
    argv = ["--dir", base_dir, "--profile", profile, "--passphrase", passphrase, command]
    for k, v in kwargs.items():
        if isinstance(v, list):
            argv.extend(v)
        else:
            argv.append(str(v))
    return parser.parse_args(argv)


def test_cmd_set_creates_new_vault(base_dir):
    args = make_args(base_dir, "set", pairs=["FOO=bar"])
    cmd_set(args)
    path = profile_path("default", base_path=base_dir)
    assert path.exists()


def test_cmd_set_updates_existing_vault(base_dir):
    args = make_args(base_dir, "set", pairs=["A=1"])
    cmd_set(args)
    args2 = make_args(base_dir, "set", pairs=["B=2"])
    cmd_set(args2)
    args3 = make_args(base_dir, "get", key="A")
    # both keys should be present
    from envoy import vault
    env = vault.load(str(profile_path("default", base_path=base_dir)), "secret")
    assert env["A"] == "1"
    assert env["B"] == "2"


def test_cmd_set_invalid_pair_exits(base_dir):
    args = make_args(base_dir, "set", pairs=["NOEQUALS"])
    with pytest.raises(SystemExit):
        cmd_set(args)


def test_cmd_get_returns_value(base_dir, capsys):
    args = make_args(base_dir, "set", pairs=["MY_KEY=hello"])
    cmd_set(args)
    args2 = make_args(base_dir, "get", key="MY_KEY")
    cmd_get(args2)
    captured = capsys.readouterr()
    assert "hello" in captured.out


def test_cmd_get_missing_profile_exits(base_dir):
    args = make_args(base_dir, "get", profile="ghost", key="X")
    with pytest.raises(SystemExit):
        cmd_get(args)


def test_cmd_list_shows_all_keys(base_dir, capsys):
    args = make_args(base_dir, "set", pairs=["X=1", "Y=2"])
    cmd_set(args)
    args2 = make_args(base_dir, "list")
    cmd_list(args2)
    out = capsys.readouterr().out
    assert "X=1" in out
    assert "Y=2" in out


def test_cmd_profiles_lists_names(base_dir, capsys):
    for name in ["dev", "prod"](base_dir, "set", profile=name, pairs=["K=V"])
        cmd_set(args)
    args2 = make_args(base_dir, "profiles")
    cmd_profiles(args2)
    out = capsys.readouterr().out
    assert "dev" in out
    assert "prod" in out


def test_cmd_delete_profile(base_dir, capsys):
    args = make_args(base_dir, "set", profile="temp", pairs=["K=V"])
    cmd_set(args)
    del_args = make_args(base_dir, "delete-profile", profile="temp")
    cmd_delete_profile(del_args)
    assert not profile_path("temp", base_path=base_dir).exists()


def test_cmd_delete_profile_missing_exits(base_dir):
    del_args = make_args(base_dir, "delete-profile", profile="nonexistent")
    with pytest.raises(SystemExit):
        cmd_delete_profile(del_args)
