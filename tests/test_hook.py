"""Tests for envoy/hook.py"""

import pytest
from envoy.hook import add_hook, remove_hook, list_hooks, run_hooks, HOOK_EVENTS


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_add_hook_creates_index(base_dir):
    add_hook(base_dir, "post-set", "echo hello")
    hooks = list_hooks(base_dir)
    assert "echo hello" in hooks.get("post-set", [])


def test_add_hook_idempotent(base_dir):
    add_hook(base_dir, "post-set", "echo hello")
    add_hook(base_dir, "post-set", "echo hello")
    hooks = list_hooks(base_dir)
    assert hooks["post-set"].count("echo hello") == 1


def test_add_multiple_hooks_same_event(base_dir):
    add_hook(base_dir, "post-set", "echo one")
    add_hook(base_dir, "post-set", "echo two")
    hooks = list_hooks(base_dir)
    assert "echo one" in hooks["post-set"]
    assert "echo two" in hooks["post-set"]


def test_add_hook_invalid_event_raises(base_dir):
    with pytest.raises(ValueError, match="Unknown event"):
        add_hook(base_dir, "on-explode", "echo boom")


def test_remove_hook_returns_true(base_dir):
    add_hook(base_dir, "pre-set", "echo before")
    result = remove_hook(base_dir, "pre-set", "echo before")
    assert result is True
    hooks = list_hooks(base_dir)
    assert "echo before" not in hooks.get("pre-set", [])


def test_remove_missing_hook_returns_false(base_dir):
    result = remove_hook(base_dir, "pre-set", "echo missing")
    assert result is False


def test_list_hooks_empty_when_no_file(base_dir):
    hooks = list_hooks(base_dir)
    assert hooks == {}


def test_list_hooks_filtered_by_event(base_dir):
    add_hook(base_dir, "post-set", "echo a")
    add_hook(base_dir, "post-rotate", "echo b")
    hooks = list_hooks(base_dir, event="post-set")
    assert "post-set" in hooks
    assert "post-rotate" not in hooks


def test_run_hooks_executes_commands(base_dir):
    add_hook(base_dir, "post-load", "exit 0")
    codes = run_hooks(base_dir, "post-load")
    assert codes == [0]


def test_run_hooks_returns_empty_for_no_hooks(base_dir):
    codes = run_hooks(base_dir, "post-load")
    assert codes == []


def test_run_hooks_passes_env(base_dir, monkeypatch):
    add_hook(base_dir, "pre-load", "exit 0")
    codes = run_hooks(base_dir, "pre-load", env={"MY_VAR": "1"})
    assert codes == [0]
