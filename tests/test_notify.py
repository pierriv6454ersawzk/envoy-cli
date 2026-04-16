"""Tests for envoy.notify module."""
from __future__ import annotations
import pytest
from pathlib import Path
from envoy import notify


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_set_notify_creates_config(base_dir):
    notify.set_notify(base_dir, "on_set", "stdout")
    config = notify.list_notify(base_dir)
    assert "on_set" in config
    assert config["on_set"][0]["channel"] == "stdout"


def test_set_notify_invalid_channel_raises(base_dir):
    with pytest.raises(ValueError, match="Invalid channel"):
        notify.set_notify(base_dir, "on_set", "sms")


def test_set_notify_idempotent(base_dir):
    notify.set_notify(base_dir, "on_set", "stdout")
    notify.set_notify(base_dir, "on_set", "stdout")
    config = notify.list_notify(base_dir)
    assert len(config["on_set"]) == 1


def test_set_notify_multiple_channels(base_dir, tmp_path):
    log = str(tmp_path / "log.txt")
    notify.set_notify(base_dir, "on_delete", "stdout")
    notify.set_notify(base_dir, "on_delete", "file", target=log)
    config = notify.list_notify(base_dir, "on_delete")
    assert len(config["on_delete"]) == 2


def test_remove_notify_returns_true(base_dir):
    notify.set_notify(base_dir, "on_set", "stdout")
    result = notify.remove_notify(base_dir, "on_set", "stdout")
    assert result is True
    config = notify.list_notify(base_dir)
    assert config["on_set"] == []


def test_remove_notify_missing_returns_false(base_dir):
    result = notify.remove_notify(base_dir, "on_set", "stdout")
    assert result is False


def test_list_notify_filtered_by_event(base_dir):
    notify.set_notify(base_dir, "on_set", "stdout")
    notify.set_notify(base_dir, "on_delete", "stdout")
    result = notify.list_notify(base_dir, "on_set")
    assert "on_set" in result
    assert "on_delete" not in result


def test_dispatch_stdout(base_dir, capsys):
    notify.set_notify(base_dir, "on_set", "stdout")
    dispatched = notify.dispatch(base_dir, "on_set", "KEY was set")
    assert "stdout" in dispatched
    captured = capsys.readouterr()
    assert "KEY was set" in captured.out


def test_dispatch_file(base_dir, tmp_path):
    log = str(tmp_path / "events.log")
    notify.set_notify(base_dir, "on_set", "file", target=log)
    notify.dispatch(base_dir, "on_set", "KEY was set")
    content = Path(log).read_text()
    assert "KEY was set" in content


def test_dispatch_no_handlers_returns_empty(base_dir):
    result = notify.dispatch(base_dir, "on_set", "hello")
    assert result == []
