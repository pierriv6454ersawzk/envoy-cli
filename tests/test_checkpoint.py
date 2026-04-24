"""Tests for envoy.checkpoint and envoy.cli_checkpoint."""

from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from envoy.checkpoint import (
    CheckpointError,
    create_checkpoint,
    delete_checkpoint,
    list_checkpoints,
    restore_checkpoint,
)
from envoy.vault import save, load


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(profile, passphrase, env, base_dir):
    save(profile, passphrase, env, base_dir)


# ---------------------------------------------------------------------------
# Core module tests
# ---------------------------------------------------------------------------

def test_create_checkpoint_returns_name(base_dir):
    _seed("dev", "pass", {"KEY": "val"}, base_dir)
    name = create_checkpoint("dev", "pass", "v1", base_dir)
    assert name == "v1"


def test_create_checkpoint_appears_in_list(base_dir):
    _seed("dev", "pass", {"A": "1"}, base_dir)
    create_checkpoint("dev", "pass", "alpha", base_dir)
    entries = list_checkpoints("dev", base_dir)
    assert any(e["name"] == "alpha" for e in entries)


def test_list_checkpoints_empty_when_none(base_dir):
    _seed("dev", "pass", {}, base_dir)
    assert list_checkpoints("dev", base_dir) == []


def test_create_checkpoint_stores_key_count(base_dir):
    _seed("dev", "pass", {"X": "1", "Y": "2"}, base_dir)
    create_checkpoint("dev", "pass", "snap", base_dir)
    entries = list_checkpoints("dev", base_dir)
    assert entries[0]["key_count"] == 2


def test_restore_checkpoint_reverts_env(base_dir):
    _seed("dev", "pass", {"KEY": "original"}, base_dir)
    create_checkpoint("dev", "pass", "before", base_dir)
    _seed("dev", "pass", {"KEY": "changed"}, base_dir)
    restore_checkpoint("dev", "before", "pass", base_dir)
    env = load("dev", "pass", base_dir)
    assert env["KEY"] == "original"


def test_restore_missing_checkpoint_raises(base_dir):
    _seed("dev", "pass", {}, base_dir)
    with pytest.raises(CheckpointError, match="not found"):
        restore_checkpoint("dev", "ghost", "pass", base_dir)


def test_delete_checkpoint_removes_entry(base_dir):
    _seed("dev", "pass", {"K": "v"}, base_dir)
    create_checkpoint("dev", "pass", "tmp", base_dir)
    delete_checkpoint("dev", "tmp", base_dir)
    assert list_checkpoints("dev", base_dir) == []


def test_delete_missing_checkpoint_raises(base_dir):
    _seed("dev", "pass", {}, base_dir)
    with pytest.raises(CheckpointError):
        delete_checkpoint("dev", "nonexistent", base_dir)


def test_create_checkpoint_missing_profile_raises(base_dir):
    with pytest.raises(CheckpointError, match="does not exist"):
        create_checkpoint("missing", "pass", "v1", base_dir)


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def make_args(**kwargs):
    defaults = {"base_dir": None, "passphrase": "secret"}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_checkpoint_create_prints_confirmation(base_dir, capsys):
    from envoy.cli_checkpoint import cmd_checkpoint_create
    _seed("dev", "secret", {"K": "v"}, base_dir)
    args = make_args(profile="dev", name="v1", base_dir=base_dir)
    cmd_checkpoint_create(args)
    out = capsys.readouterr().out
    assert "v1" in out and "dev" in out


def test_cmd_checkpoint_list_shows_entries(base_dir, capsys):
    from envoy.cli_checkpoint import cmd_checkpoint_list
    _seed("dev", "secret", {"K": "v"}, base_dir)
    create_checkpoint("dev", "secret", "snap1", base_dir)
    args = make_args(profile="dev", base_dir=base_dir)
    cmd_checkpoint_list(args)
    out = capsys.readouterr().out
    assert "snap1" in out


def test_cmd_checkpoint_restore_success(base_dir, capsys):
    from envoy.cli_checkpoint import cmd_checkpoint_restore
    _seed("dev", "secret", {"K": "before"}, base_dir)
    create_checkpoint("dev", "secret", "pre", base_dir)
    _seed("dev", "secret", {"K": "after"}, base_dir)
    args = make_args(profile="dev", name="pre", base_dir=base_dir)
    cmd_checkpoint_restore(args)
    env = load("dev", "secret", base_dir)
    assert env["K"] == "before"


def test_cmd_checkpoint_delete_missing_exits(base_dir):
    from envoy.cli_checkpoint import cmd_checkpoint_delete
    _seed("dev", "secret", {}, base_dir)
    args = make_args(profile="dev", name="ghost", base_dir=base_dir)
    with pytest.raises(SystemExit):
        cmd_checkpoint_delete(args)
