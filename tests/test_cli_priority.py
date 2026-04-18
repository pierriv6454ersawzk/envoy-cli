import pytest
from types import SimpleNamespace
from envoy.cli_priority import cmd_priority_set, cmd_priority_remove, cmd_priority_show, cmd_priority_list
from envoy.vault import save
from envoy.priority import get_priority


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile="default"):
    save({"K": "v"}, profile, "pass", base_dir)


def make_args(base_dir, **kwargs):
    return SimpleNamespace(base_dir=base_dir, **kwargs)


def test_cmd_priority_set_prints_confirmation(base_dir, capsys):
    _seed(base_dir)
    cmd_priority_set(make_args(base_dir, profile="default", priority=5))
    out = capsys.readouterr().out
    assert "default" in out
    assert "5" in out


def test_cmd_priority_set_invalid_priority_exits(base_dir):
    _seed(base_dir)
    with pytest.raises(SystemExit):
        cmd_priority_set(make_args(base_dir, profile="default", priority="abc"))


def test_cmd_priority_set_missing_profile_exits(base_dir):
    with pytest.raises(SystemExit):
        cmd_priority_set(make_args(base_dir, profile="ghost", priority=1))


def test_cmd_priority_remove_prints_confirmation(base_dir, capsys):
    _seed(base_dir)
    cmd_priority_remove(make_args(base_dir, profile="default"))
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_priority_show_displays_value(base_dir, capsys):
    _seed(base_dir)
    from envoy.priority import set_priority
    set_priority(base_dir, "default", 42)
    cmd_priority_show(make_args(base_dir, profile="default"))
    out = capsys.readouterr().out
    assert "42" in out


def test_cmd_priority_list_empty(base_dir, capsys):
    cmd_priority_list(make_args(base_dir))
    out = capsys.readouterr().out
    assert "No priorities" in out


def test_cmd_priority_list_shows_entries(base_dir, capsys):
    for name in ["a", "b"]:
        _seed(base_dir, name)
    from envoy.priority import set_priority
    set_priority(base_dir, "a", 3)
    set_priority(base_dir, "b", 7)
    cmd_priority_list(make_args(base_dir))
    out = capsys.readouterr().out
    assert "a" in out and "b" in out
