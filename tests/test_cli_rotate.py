"""Tests for envoy.cli_rotate."""

from __future__ import annotations

import argparse
import pytest
from pathlib import Path

from envoy.vault import save, load
from envoy.profile import profile_path
from envoy.cli_rotate import cmd_rotate, register_rotate_commands


@pytest.fixture()
def base_dir(tmp_path: Path) -> Path:
    return tmp_path


def make_args(base_dir: Path, profile: str = "default", **kwargs) -> argparse.Namespace:
    return argparse.Namespace(
        base_dir=str(base_dir),
        profile=profile,
        **kwargs,
    )


def _seed(base_dir: Path, profile: str = "default", passphrase: str = "old") -> Path:
    path = profile_path(profile, base_dir=base_dir)
    save(path, {"K": "V"}, passphrase)
    return path


def test_cmd_rotate_success(base_dir):
    path = _seed(base_dir)
    args = make_args(
        base_dir,
        old_passphrase="old",
        new_passphrase="new",
        confirm_passphrase="new",
    )
    cmd_rotate(args)  # should not raise
    assert load(path, "new") == {"K": "V"}


def test_cmd_rotate_mismatched_confirm_exits(base_dir, capsys):
    _seed(base_dir)
    args = make_args(
        base_dir,
        old_passphrase="old",
        new_passphrase="new",
        confirm_passphrase="different",
    )
    with pytest.raises(SystemExit) as exc_info:
        cmd_rotate(args)
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "do not match" in captured.err


def test_cmd_rotate_wrong_old_passphrase_exits(base_dir, capsys):
    _seed(base_dir)
    args = make_args(
        base_dir,
        old_passphrase="wrong",
        new_passphrase="new",
        confirm_passphrase="new",
    )
    with pytest.raises(SystemExit) as exc_info:
        cmd_rotate(args)
    assert exc_info.value.code == 1


def test_cmd_rotate_missing_profile_exits(base_dir, capsys):
    args = make_args(
        base_dir,
        profile="ghost",
        old_passphrase="old",
        new_passphrase="new",
        confirm_passphrase="new",
    )
    with pytest.raises(SystemExit) as exc_info:
        cmd_rotate(args)
    assert exc_info.value.code == 1


def test_register_rotate_commands():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_rotate_commands(sub)
    parsed = parser.parse_args(["rotate", "staging"])
    assert parsed.profile == "staging"
    assert parsed.func is cmd_rotate
