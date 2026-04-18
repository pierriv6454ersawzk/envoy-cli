"""Tests for envoy.depend and envoy.cli_depend."""

import pytest
from pathlib import Path
from envoy.depend import (
    add_dependency, remove_dependency, get_dependencies,
    get_dependents, list_all, DependencyError
)
from envoy.vault import save
from envoy.cli_depend import cmd_depend_add, cmd_depend_show, cmd_depend_reverse, cmd_depend_list


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile):
    from envoy.profile import profile_path
    save(profile_path(base_dir, profile), "pass", {"KEY": "val"})


def test_add_dependency_creates_entry(base_dir):
    _seed(base_dir, "app")
    _seed(base_dir, "base")
    add_dependency(base_dir, "app", "base")
    assert "base" in get_dependencies(base_dir, "app")


def test_add_dependency_idempotent(base_dir):
    _seed(base_dir, "app")
    _seed(base_dir, "base")
    add_dependency(base_dir, "app", "base")
    add_dependency(base_dir, "app", "base")
    assert get_dependencies(base_dir, "app").count("base") == 1


def test_add_dependency_self_raises(base_dir):
    _seed(base_dir, "app")
    with pytest.raises(DependencyError, match="itself"):
        add_dependency(base_dir, "app", "app")


def test_add_dependency_missing_profile_raises(base_dir):
    _seed(base_dir, "app")
    with pytest.raises(DependencyError):
        add_dependency(base_dir, "app", "ghost")


def test_remove_dependency(base_dir):
    _seed(base_dir, "app")
    _seed(base_dir, "base")
    add_dependency(base_dir, "app", "base")
    remove_dependency(base_dir, "app", "base")
    assert get_dependencies(base_dir, "app") == []


def test_get_dependents(base_dir):
    _seed(base_dir, "app")
    _seed(base_dir, "worker")
    _seed(base_dir, "base")
    add_dependency(base_dir, "app", "base")
    add_dependency(base_dir, "worker", "base")
    dependents = get_dependents(base_dir, "base")
    assert "app" in dependents
    assert "worker" in dependents


def test_list_all_returns_all(base_dir):
    _seed(base_dir, "app")
    _seed(base_dir, "base")
    _seed(base_dir, "worker")
    add_dependency(base_dir, "app", "base")
    add_dependency(base_dir, "worker", "base")
    all_deps = list_all(base_dir)
    assert "app" in all_deps
    assert "worker" in all_deps


def test_get_dependencies_empty_when_missing(base_dir):
    _seed(base_dir, "app")
    assert get_dependencies(base_dir, "app") == []


class Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_cmd_depend_add_prints_confirmation(base_dir, capsys):
    _seed(base_dir, "app")
    _seed(base_dir, "base")
    args = Args(base_dir=base_dir, profile="app", depends_on="base")
    cmd_depend_add(args)
    assert "app" in capsys.readouterr().out


def test_cmd_depend_add_missing_profile_exits(base_dir):
    _seed(base_dir, "app")
    args = Args(base_dir=base_dir, profile="app", depends_on="ghost")
    with pytest.raises(SystemExit):
        cmd_depend_add(args)
