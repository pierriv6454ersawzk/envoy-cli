"""Tests for envoy.merge and envoy.cli_merge."""
import argparse
import pytest
from pathlib import Path
from envoy.vault import save
from envoy.merge import merge_profiles, MergeError
from envoy.cli_merge import cmd_merge

PASS = "secret"


@pytest.fixture
def base_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def _seed(base_dir: str, profile: str, data: dict) -> None:
    from envoy.profile import profile_path
    p = profile_path(profile, base_dir)
    save(str(p), data, PASS)


def test_merge_combines_keys(base_dir):
    _seed(base_dir, "src", {"A": "1", "B": "2"})
    _seed(base_dir, "dst", {"C": "3"})
    stats = merge_profiles(["src"], "dst", PASS, base_dir)
    assert stats["src"] == 2


def test_merge_overwrite_default(base_dir):
    _seed(base_dir, "src", {"KEY": "new"})
    _seed(base_dir, "dst", {"KEY": "old"})
    merge_profiles(["src"], "dst", PASS, base_dir, overwrite=True)
    from envoy.vault import load
    from envoy.profile import profile_path
    result = load(str(profile_path("dst", base_dir)), PASS)
    assert result["KEY"] == "new"


def test_merge_no_overwrite(base_dir):
    _seed(base_dir, "src", {"KEY": "new"})
    _seed(base_dir, "dst", {"KEY": "old"})
    stats = merge_profiles(["src"], "dst", PASS, base_dir, overwrite=False)
    assert stats["src"] == 0
    from envoy.vault import load
    from envoy.profile import profile_path
    result = load(str(profile_path("dst", base_dir)), PASS)
    assert result["KEY"] == "old"


def test_merge_missing_target_raises(base_dir):
    _seed(base_dir, "src", {"A": "1"})
    with pytest.raises(MergeError, match="Target"):
        merge_profiles(["src"], "ghost", PASS, base_dir)


def test_merge_missing_source_raises(base_dir):
    _seed(base_dir, "dst", {"A": "1"})
    with pytest.raises(MergeError, match="Source"):
        merge_profiles(["ghost"], "dst", PASS, base_dir)


def test_merge_same_source_target_raises(base_dir):
    _seed(base_dir, "env", {"A": "1"})
    with pytest.raises(MergeError, match="differ"):
        merge_profiles(["env"], "env", PASS, base_dir)


def test_cmd_merge_success(base_dir, capsys):
    _seed(base_dir, "src", {"X": "1"})
    _seed(base_dir, "dst", {})
    args = argparse.Namespace(
        sources=["src"], target="dst", passphrase=PASS,
        base_dir=base_dir, no_overwrite=False
    )
    cmd_merge(args)
    captured = capsys.readouterr()
    assert "1 key(s)" in captured.out


def test_cmd_merge_missing_profile_exits(base_dir):
    _seed(base_dir, "dst", {})
    args = argparse.Namespace(
        sources=["missing"], target="dst", passphrase=PASS,
        base_dir=base_dir, no_overwrite=False
    )
    with pytest.raises(SystemExit):
        cmd_merge(args)
