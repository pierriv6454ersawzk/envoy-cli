"""Tests for envoy.cli_audit commands."""

import argparse
import pytest
from envoy.audit import record
from envoy.cli_audit import cmd_audit_show, cmd_audit_clear


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(**kwargs):
    ns = argparse.Namespace(base_dir=None, profile=None, force=False)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_audit_show_empty(base_dir, capsys):
    args = make_args(base_dir=base_dir)
    cmd_audit_show(args)
    captured = capsys.readouterr()
    assert "No audit log entries" in captured.out


def test_audit_show_displays_entries(base_dir, capsys):
    record("set", "default", key="FOO", base_dir=base_dir)
    record("get", "default", key="FOO", base_dir=base_dir)
    args = make_args(base_dir=base_dir)
    cmd_audit_show(args)
    captured = capsys.readouterr()
    assert "set" in captured.out
    assert "get" in captured.out
    assert "FOO" in captured.out


def test_audit_show_filters_by_profile(base_dir, capsys):
    record("set", "default", key="A", base_dir=base_dir)
    record("set", "staging", key="B", base_dir=base_dir)
    args = make_args(base_dir=base_dir, profile="staging")
    cmd_audit_show(args)
    captured = capsys.readouterr()
    assert "staging" in captured.out
    assert "default" not in captured.out


def test_audit_show_no_entries_for_profile(base_dir, capsys):
    record("set", "default", key="A", base_dir=base_dir)
    args = make_args(base_dir=base_dir, profile="nonexistent")
    cmd_audit_show(args)
    captured = capsys.readouterr()
    assert "No entries for profile" in captured.out


def test_audit_clear_with_force(base_dir, capsys):
    record("set", "default", key="X", base_dir=base_dir)
    args = make_args(base_dir=base_dir, force=True)
    cmd_audit_clear(args)
    captured = capsys.readouterr()
    assert "cleared" in captured.out
    from envoy.audit import read_log
    assert read_log(base_dir=base_dir) == []


def test_audit_clear_aborted(base_dir, capsys, monkeypatch):
    record("set", "default", key="X", base_dir=base_dir)
    monkeypatch.setattr("builtins.input", lambda _: "n")
    args = make_args(base_dir=base_dir, force=False)
    cmd_audit_clear(args)
    captured = capsys.readouterr()
    assert "Aborted" in captured.out
    from envoy.audit import read_log
    assert len(read_log(base_dir=base_dir)) == 1
