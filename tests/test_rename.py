"""Tests for envoy.rename."""

from __future__ import annotations

import argparse
import sys
import pytest

from envoy.vault import save, load
from envoy.rename import rename_key, RenameError
from envoy.cli_rename import cmd_rename, register_rename_commands


PASS = "hunter2"


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile="default", env=None):
    if env is None:
        env = {"API_KEY": "abc123", "DB_HOST": "localhost"}
    save(profile, env, PASS, base_dir=base_dir)
    return env


def make_args(base_dir, **kwargs):
    defaults = dict(
        profile="default",
        old_key="API_KEY",
        new_key="API_TOKEN",
        passphrase=PASS,
        overwrite=False,
        base_dir=base_dir,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# --- unit tests for rename_key ---

def test_rename_key_renames_successfully(base_dir):
    _seed(base_dir)
    env = rename_key("default", "API_KEY", "API_TOKEN", PASS, base_dir=base_dir)
    assert "API_TOKEN" in env
    assert "API_KEY" not in env


def test_rename_key_preserves_value(base_dir):
    _seed(base_dir)
    env = rename_key("default", "API_KEY", "API_TOKEN", PASS, base_dir=base_dir)
    assert env["API_TOKEN"] == "abc123"


def test_rename_key_persists_to_vault(base_dir):
    _seed(base_dir)
    rename_key("default", "API_KEY", "API_TOKEN", PASS, base_dir=base_dir)
    reloaded = load("default", PASS, base_dir=base_dir)
    assert "API_TOKEN" in reloaded
    assert "API_KEY" not in reloaded


def test_rename_key_missing_old_key_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(RenameError, match="not found"):
        rename_key("default", "MISSING", "NEW_KEY", PASS, base_dir=base_dir)


def test_rename_key_same_name_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(RenameError, match="identical"):
        rename_key("default", "API_KEY", "API_KEY", PASS, base_dir=base_dir)


def test_rename_key_existing_new_key_raises_without_overwrite(base_dir):
    _seed(base_dir)
    with pytest.raises(RenameError, match="already exists"):
        rename_key("default", "API_KEY", "DB_HOST", PASS, base_dir=base_dir)


def test_rename_key_existing_new_key_allowed_with_overwrite(base_dir):
    _seed(base_dir)
    env = rename_key(
        "default", "API_KEY", "DB_HOST", PASS,
        base_dir=base_dir, overwrite=True
    )
    assert env["DB_HOST"] == "abc123"


# --- CLI tests ---

def test_cmd_rename_success(base_dir, capsys):
    _seed(base_dir)
    args = make_args(base_dir)
    cmd_rename(args)
    out = capsys.readouterr().out
    assert "API_KEY" in out
    assert "API_TOKEN" in out


def test_cmd_rename_missing_key_exits(base_dir):
    _seed(base_dir)
    args = make_args(base_dir, old_key="DOES_NOT_EXIST")
    with pytest.raises(SystemExit) as exc_info:
        cmd_rename(args)
    assert exc_info.value.code == 1


def test_register_rename_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_rename_commands(subparsers)
    parsed = parser.parse_args(
        ["rename", "dev", "OLD", "NEW", "--passphrase", "secret"]
    )
    assert parsed.profile == "dev"
    assert parsed.old_key == "OLD"
    assert parsed.new_key == "NEW"
