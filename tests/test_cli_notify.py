"""Tests for envoy.cli_notify module."""
from __future__ import annotations
import argparse
import pytest
from envoy import notify
from envoy.cli_notify import cmd_notify_add, cmd_notify_remove, cmd_notify_list, cmd_notify_dispatch


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(base_dir, **kwargs):
    ns = argparse.Namespace(base_dir=base_dir, profile="default", **kwargs)
    return ns


def test_cmd_notify_add_prints_confirmation(base_dir, capsys):
    args = make_args(base_dir, event="on_set", channel="stdout", target=None)
    cmd_notify_add(args)
    out = capsys.readouterr().out
    assert "on_set" in out
    assert "stdout" in out


def test_cmd_notify_add_invalid_channel_exits(base_dir):
    args = make_args(base_dir, event="on_set", channel="telegram", target=None)
    with pytest.raises(SystemExit):
        cmd_notify_add(args)


def test_cmd_notify_remove_prints_confirmation(base_dir, capsys):
    notify.set_notify(base_dir, "on_set", "stdout")
    args = make_args(base_dir, event="on_set", channel="stdout")
    cmd_notify_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_cmd_notify_remove_missing_prints_message(base_dir, capsys):
    args = make_args(base_dir, event="on_set", channel="stdout")
    cmd_notify_remove(args)
    out = capsys.readouterr().out
    assert "No matching" in out


def test_cmd_notify_list_empty(base_dir, capsys):
    args = make_args(base_dir, event=None)
    cmd_notify_list(args)
    out = capsys.readouterr().out
    assert "No notifications" in out


def test_cmd_notify_list_shows_entries(base_dir, capsys):
    notify.set_notify(base_dir, "on_delete", "stdout")
    args = make_args(base_dir, event=None)
    cmd_notify_list(args)
    out = capsys.readouterr().out
    assert "on_delete" in out
    assert "stdout" in out


def test_cmd_notify_dispatch_stdout(base_dir, capsys):
    notify.set_notify(base_dir, "on_set", "stdout")
    args = make_args(base_dir, event="on_set", message="test message")
    cmd_notify_dispatch(args)
    out = capsys.readouterr().out
    assert "test message" in out or "Dispatched" in out


def test_cmd_notify_dispatch_no_handlers(base_dir, capsys):
    args = make_args(base_dir, event="on_set", message="nothing")
    cmd_notify_dispatch(args)
    out = capsys.readouterr().out
    assert "No notifications dispatched" in out
