"""Tests for envoy.cli_sync commands."""

import sys
import pytest
from pathlib import Path
from types import SimpleNamespace

from envoy.vault import save
from envoy.profile import profile_path
from envoy.cli_sync import cmd_push, cmd_pull, cmd_diff, cmd_remote_set, cmd_remote_show


PASSPHRASE = "cli-sync-pass"


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(**kwargs):
    defaults = {"passphrase": PASSPHRASE, "base_dir": None}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_push_success(base_dir, tmp_path, capsys):
    local = profile_path("prod", base_dir)
    save(str(local), PASSPHRASE, {"KEY": "val"})
    remote = str(tmp_path / "remote.enc")

    args = make_args(profile="prod", remote=remote, base_dir=base_dir)
    cmd_push(args)

    captured = capsys.readouterr()
    assert "Pushed" in captured.out
    assert Path(remote).exists()


def test_cmd_push_missing_profile_exits(base_dir, tmp_path):
    args = make_args(profile="ghost", remote=str(tmp_path / "r.enc"), base_dir=base_dir)
    with pytest.raises(SystemExit):
        cmd_push(args)


def test_cmd_pull_success(base_dir, tmp_path, capsys):
    remote = str(tmp_path / "remote.enc")
    save(remote, PASSPHRASE, {"PULLED": "yes"})

    args = make_args(profile="staging", remote=remote, base_dir=base_dir)
    cmd_pull(args)

    captured = capsys.readouterr()
    assert "Pulled" in captured.out
    assert profile_path("staging", base_dir).exists()


def test_cmd_pull_missing_remote_exits(base_dir, tmp_path):
    args = make_args(profile="staging", remote=str(tmp_path / "nope.enc"), base_dir=base_dir)
    with pytest.raises(SystemExit):
        cmd_pull(args)


def test_cmd_diff_shows_differences(base_dir, tmp_path, capsys):
    local = profile_path("dev", base_dir)
    save(str(local), PASSPHRASE, {"A": "local_val"})
    remote = str(tmp_path / "r.enc")
    save(remote, PASSPHRASE, {"A": "remote_val"})

    args = make_args(profile="dev", remote=remote, base_dir=base_dir)
    cmd_diff(args)

    captured = capsys.readouterr()
    assert "A" in captured.out
    assert "local_val" in captured.out


def test_cmd_diff_no_diff(base_dir, tmp_path, capsys):
    local = profile_path("dev", base_dir)
    save(str(local), PASSPHRASE, {"X": "same"})
    remote = str(tmp_path / "r.enc")
    save(remote, PASSPHRASE, {"X": "same"})

    args = make_args(profile="dev", remote=remote, base_dir=base_dir)
    cmd_diff(args)

    captured = capsys.readouterr()
    assert "No differences" in captured.out


def test_cmd_remote_set_and_show(base_dir, capsys):
    args = make_args(key="backend", value="s3", base_dir=base_dir)
    cmd_remote_set(args)

    args2 = make_args(base_dir=base_dir)
    cmd_remote_show(args2)

    captured = capsys.readouterr()
    assert "backend=s3" in captured.out


def test_cmd_remote_show_empty(base_dir, capsys):
    args = make_args(base_dir=base_dir)
    cmd_remote_show(args)
    captured = capsys.readouterr()
    assert "No remote configuration" in captured.out
