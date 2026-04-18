import pytest
import argparse
import sys
from envoy.cli_note import cmd_note_set, cmd_note_get, cmd_note_remove, cmd_note_list
from envoy.vault import save
from envoy.note import set_note


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(base_dir, profile="default", **kwargs):
    ns = argparse.Namespace(base_dir=base_dir, profile=profile, key=None, **kwargs)
    return ns


def _seed(base_dir, profile="default"):
    save({"X": "1"}, "pass", profile=profile, base_dir=base_dir)


def test_cmd_note_set_prints_confirmation(base_dir, capsys):
    _seed(base_dir)
    args = make_args(base_dir, note="My note")
    cmd_note_set(args)
    out = capsys.readouterr().out
    assert "Note set" in out


def test_cmd_note_set_missing_profile_exits(base_dir):
    args = make_args(base_dir, profile="ghost", note="hi")
    with pytest.raises(SystemExit):
        cmd_note_set(args)


def test_cmd_note_get_prints_note(base_dir, capsys):
    _seed(base_dir)
    set_note("default", "hello world", base_dir=base_dir)
    args = make_args(base_dir)
    cmd_note_get(args)
    out = capsys.readouterr().out
    assert "hello world" in out


def test_cmd_note_get_missing_prints_message(base_dir, capsys):
    _seed(base_dir)
    args = make_args(base_dir)
    cmd_note_get(args)
    out = capsys.readouterr().out
    assert "No note" in out


def test_cmd_note_remove_confirms(base_dir, capsys):
    _seed(base_dir)
    set_note("default", "to remove", base_dir=base_dir)
    args = make_args(base_dir)
    cmd_note_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_note_list_shows_entries(base_dir, capsys):
    _seed(base_dir)
    set_note("default", "profile note", base_dir=base_dir)
    set_note("default", "key note", key="API", base_dir=base_dir)
    args = make_args(base_dir)
    cmd_note_list(args)
    out = capsys.readouterr().out
    assert "profile note" in out
    assert "key note" in out


def test_cmd_note_list_empty_message(base_dir, capsys):
    _seed(base_dir)
    args = make_args(base_dir)
    cmd_note_list(args)
    out = capsys.readouterr().out
    assert "No notes" in out
