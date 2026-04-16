"""Tests for envoy.group."""
import pytest
from pathlib import Path
from envoy.group import (
    add_to_group, remove_from_group, list_groups,
    group_members, delete_group, profile_groups,
)
from envoy.vault import save


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile, passphrase="pass"):
    save({"KEY": "val"}, profile, passphrase, base_dir=base_dir)


def test_add_to_group_creates_entry(base_dir):
    _seed(base_dir, "dev")
    add_to_group("team-a", "dev", base_dir=base_dir)
    assert "dev" in group_members("team-a", base_dir=base_dir)


def test_add_to_group_idempotent(base_dir):
    _seed(base_dir, "dev")
    add_to_group("team-a", "dev", base_dir=base_dir)
    add_to_group("team-a", "dev", base_dir=base_dir)
    assert group_members("team-a", base_dir=base_dir).count("dev") == 1


def test_add_to_group_missing_profile_raises(base_dir):
    with pytest.raises(ValueError, match="does not exist"):
        add_to_group("team-a", "ghost", base_dir=base_dir)


def test_list_groups_empty(base_dir):
    assert list_groups(base_dir=base_dir) == []


def test_list_groups_returns_sorted(base_dir):
    _seed(base_dir, "dev")
    _seed(base_dir, "prod")
    add_to_group("z-group", "dev", base_dir=base_dir)
    add_to_group("a-group", "prod", base_dir=base_dir)
    assert list_groups(base_dir=base_dir) == ["a-group", "z-group"]


def test_remove_from_group(base_dir):
    _seed(base_dir, "dev")
    add_to_group("team-a", "dev", base_dir=base_dir)
    remove_from_group("team-a", "dev", base_dir=base_dir)
    assert group_members("team-a", base_dir=base_dir) == []


def test_remove_from_group_deletes_empty_group(base_dir):
    _seed(base_dir, "dev")
    add_to_group("team-a", "dev", base_dir=base_dir)
    remove_from_group("team-a", "dev", base_dir=base_dir)
    assert "team-a" not in list_groups(base_dir=base_dir)


def test_delete_group(base_dir):
    _seed(base_dir, "dev")
    add_to_group("team-a", "dev", base_dir=base_dir)
    delete_group("team-a", base_dir=base_dir)
    assert list_groups(base_dir=base_dir) == []


def test_profile_groups(base_dir):
    _seed(base_dir, "dev")
    add_to_group("team-a", "dev", base_dir=base_dir)
    add_to_group("team-b", "dev", base_dir=base_dir)
    assert profile_groups("dev", base_dir=base_dir) == ["team-a", "team-b"]


def test_profile_groups_not_member(base_dir):
    _seed(base_dir, "dev")
    assert profile_groups("dev", base_dir=base_dir) == []
