"""Tests for envoy.cli_archive."""

import pytest
import sys
from types import SimpleNamespace
from envoy.cli_archive import cmd_archive_create, cmd_archive_list, cmd_archive_restore, cmd_archive_delete
from envoy.vault import save
from envoy.profile import profile_path


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(base_dir, **kwargs):
    return SimpleNamespace(base_dir=base_dir, **kwargs)


def _seed(base_dir, profile="default"):
    p = profile_path(base_dir, profile)
    save(p, {"A": "1"}, passphrase="pass")


def test_cmd_archive_create_prints_name(base_dir, capsys):
    _seed(base_dir)
    args = make_args(base_dir, label="ci")
    cmd_archive_create(args)
    out = capsys.readouterr().out
    assert "Archive created" in out


def test_cmd_archive_list_empty(base_dir, capsys):
    args = make_args(base_dir)
    cmd_archive_list(args)
    out = capsys.readouterr().out
    assert "No archives found" in out


def test_cmd_archive_list_shows_entry(base_dir, capsys):
    _seed(base_dir)
    from envoy.archive import create_archive
    create_archive(base_dir, label="myarchive")
    args = make_args(base_dir)
    cmd_archive_list(args)
    out = capsys.readouterr().out
    assert "myarchive" in out


def test_cmd_archive_restore_success(base_dir, capsys):
    _seed(base_dir)
    from envoy.archive import create_archive
    path = create_archive(base_dir)
    args = make_args(base_dir, name=path.name)
    cmd_archive_restore(args)
    out = capsys.readouterr().out
    assert "Restored" in out


def test_cmd_archive_restore_missing_exits(base_dir):
    args = make_args(base_dir, name="missing.tar.gz")
    with pytest.raises(SystemExit):
        cmd_archive_restore(args)


def test_cmd_archive_delete_success(base_dir, capsys):
    _seed(base_dir)
    from envoy.archive import create_archive
    path = create_archive(base_dir)
    args = make_args(base_dir, name=path.name)
    cmd_archive_delete(args)
    out = capsys.readouterr().out
    assert "Deleted" in out


def test_cmd_archive_delete_missing_exits(base_dir):
    args = make_args(base_dir, name="nope.tar.gz")
    with pytest.raises(SystemExit):
        cmd_archive_delete(args)
