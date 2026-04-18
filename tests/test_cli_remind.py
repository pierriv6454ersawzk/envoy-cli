"""Tests for envoy.cli_remind."""
import sys
import time
import pytest
from types import SimpleNamespace
from envoy.vault import save
from envoy.cli_remind import cmd_remind_set, cmd_remind_remove, cmd_remind_show, cmd_remind_list, cmd_remind_due


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile="default"):
    save({"KEY": "val"}, profile, "pass", base_dir)


def make_args(**kwargs):
    return SimpleNamespace(**kwargs)


def test_cmd_remind_set_prints_confirmation(base_dir, capsys):
    _seed(base_dir)
    due = str(time.time() + 3600)
    args = make_args(base_dir=base_dir, profile="default", key="KEY", message="Check!", due=due)
    cmd_remind_set(args)
    out = capsys.readouterr().out
    assert "Reminder set" in out


def test_cmd_remind_set_invalid_due_exits(base_dir, capsys):
    _seed(base_dir)
    args = make_args(base_dir=base_dir, profile="default", key="KEY", message="msg", due="not-a-float")
    with pytest.raises(SystemExit):
        cmd_remind_set(args)


def test_cmd_remind_set_past_due_exits(base_dir, capsys):
    _seed(base_dir)
    args = make_args(base_dir=base_dir, profile="default", key="KEY", message="msg", due=str(time.time() - 10))
    with pytest.raises(SystemExit):
        cmd_remind_set(args)


def test_cmd_remind_remove_prints_confirmation(base_dir, capsys):
    _seed(base_dir)
    from envoy.remind import set_reminder
    set_reminder(base_dir, "default", "KEY", "msg", time.time() + 100)
    args = make_args(base_dir=base_dir, profile="default", key="KEY")
    cmd_remind_remove(args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_remind_show_prints_details(base_dir, capsys):
    _seed(base_dir)
    from envoy.remind import set_reminder
    set_reminder(base_dir, "default", "KEY", "Hello!", time.time() + 3600)
    args = make_args(base_dir=base_dir, profile="default", key="KEY")
    cmd_remind_show(args)
    out = capsys.readouterr().out
    assert "Hello!" in out


def test_cmd_remind_list_empty(base_dir, capsys):
    _seed(base_dir)
    args = make_args(base_dir=base_dir, profile="default")
    cmd_remind_list(args)
    out = capsys.readouterr().out
    assert "No reminders" in out


def test_cmd_remind_due_no_overdue(base_dir, capsys):
    _seed(base_dir)
    args = make_args(base_dir=base_dir, profile="default")
    cmd_remind_due(args)
    out = capsys.readouterr().out
    assert "No due reminders" in out
