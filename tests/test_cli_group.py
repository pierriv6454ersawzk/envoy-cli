"""Tests for envoy.cli_group."""
import argparse
import pytest
from envoy.cli_group import (
    cmd_group_add, cmd_group_remove, cmd_group_list,
    cmd_group_members, cmd_group_delete, cmd_group_show,
)
from envoy.vault import save


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(base_dir, **kwargs):
    ns = argparse.Namespace(base_dir=base_dir, **kwargs)
    return ns


def _seed(base_dir, profile):
    save({"K": "v"}, profile, "pass", base_dir=base_dir)


def test_cmd_group_add_prints_confirmation(base_dir, capsys):
    _seed(base_dir, "dev")
    cmd_group_add(make_args(base_dir, group="team-a", profile="dev"))
    out = capsys.readouterr().out
    assert "added" in out and "team-a" in out


def test_cmd_group_add_missing_profile_exits(base_dir):
    with pytest.raises(SystemExit):
        cmd_group_add(make_args(base_dir, group="team-a", profile="ghost"))


def test_cmd_group_remove_prints_confirmation(base_dir, capsys):
    _seed(base_dir, "dev")
    from envoy.group import add_to_group
    add_to_group("team-a", "dev", base_dir=base_dir)
    cmd_group_remove(make_args(base_dir, group="team-a", profile="dev"))
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_group_list_empty(base_dir, capsys):
    cmd_group_list(make_args(base_dir))
    assert "No groups" in capsys.readouterr().out


def test_cmd_group_list_shows_groups(base_dir, capsys):
    _seed(base_dir, "dev")
    from envoy.group import add_to_group
    add_to_group("team-a", "dev", base_dir=base_dir)
    cmd_group_list(make_args(base_dir))
    assert "team-a" in capsys.readouterr().out


def test_cmd_group_members_shows_profiles(base_dir, capsys):
    _seed(base_dir, "dev")
    from envoy.group import add_to_group
    add_to_group("team-a", "dev", base_dir=base_dir)
    cmd_group_members(make_args(base_dir, group="team-a"))
    assert "dev" in capsys.readouterr().out


def test_cmd_group_delete_removes_group(base_dir, capsys):
    _seed(base_dir, "dev")
    from envoy.group import add_to_group
    add_to_group("team-a", "dev", base_dir=base_dir)
    cmd_group_delete(make_args(base_dir, group="team-a"))
    assert "deleted" in capsys.readouterr().out


def test_cmd_group_show_lists_groups_for_profile(base_dir, capsys):
    _seed(base_dir, "dev")
    from envoy.group import add_to_group
    add_to_group("team-a", "dev", base_dir=base_dir)
    cmd_group_show(make_args(base_dir, profile="dev"))
    assert "team-a" in capsys.readouterr().out
