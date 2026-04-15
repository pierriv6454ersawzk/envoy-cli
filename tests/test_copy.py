"""Tests for envoy.copy and envoy.cli_copy."""

from __future__ import annotations

import argparse
import pytest

from envoy.copy import copy_keys
from envoy.vault import load, save
from envoy.profile import profile_path
from envoy.cli_copy import cmd_copy


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile, passphrase, env):
    path = profile_path(profile, base_dir=base_dir)
    save(path, env, passphrase)


# --- copy_keys unit tests ---

def test_copy_all_keys(base_dir):
    _seed(base_dir, "prod", "pass1", {"A": "1", "B": "2"})
    copied = copy_keys("prod", "staging", "pass1", "pass2", base_dir=base_dir)
    assert copied == {"A": "1", "B": "2"}
    result = load(profile_path("staging", base_dir=base_dir), "pass2")
    assert result == {"A": "1", "B": "2"}


def test_copy_specific_keys(base_dir):
    _seed(base_dir, "prod", "pass1", {"A": "1", "B": "2", "C": "3"})
    copied = copy_keys("prod", "staging", "pass1", "pass2", keys=["A", "C"], base_dir=base_dir)
    assert set(copied.keys()) == {"A", "C"}
    result = load(profile_path("staging", base_dir=base_dir), "pass2")
    assert "B" not in result


def test_copy_missing_source_raises(base_dir):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        copy_keys("ghost", "staging", "pass1", "pass2", base_dir=base_dir)


def test_copy_missing_key_raises(base_dir):
    _seed(base_dir, "prod", "pass1", {"A": "1"})
    with pytest.raises(KeyError):
        copy_keys("prod", "staging", "pass1", "pass2", keys=["NOPE"], base_dir=base_dir)


def test_copy_no_overwrite_skips_existing(base_dir):
    _seed(base_dir, "prod", "pass1", {"A": "new", "B": "2"})
    _seed(base_dir, "staging", "pass2", {"A": "old"})
    copy_keys("prod", "staging", "pass1", "pass2", overwrite=False, base_dir=base_dir)
    result = load(profile_path("staging", base_dir=base_dir), "pass2")
    assert result["A"] == "old"  # not overwritten
    assert result["B"] == "2"    # new key added


def test_copy_overwrite_replaces_existing(base_dir):
    _seed(base_dir, "prod", "pass1", {"A": "new"})
    _seed(base_dir, "staging", "pass2", {"A": "old"})
    copy_keys("prod", "staging", "pass1", "pass2", overwrite=True, base_dir=base_dir)
    result = load(profile_path("staging", base_dir=base_dir), "pass2")
    assert result["A"] == "new"


# --- cmd_copy CLI tests ---

def make_args(base_dir, **kwargs):
    defaults = dict(
        src="prod",
        dst="staging",
        src_passphrase="pass1",
        dst_passphrase="pass2",
        keys=[],
        no_overwrite=False,
        base_dir=base_dir,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_copy_success(base_dir, capsys):
    _seed(base_dir, "prod", "pass1", {"X": "10", "Y": "20"})
    cmd_copy(make_args(base_dir))
    out = capsys.readouterr().out
    assert "2 key(s)" in out
    assert "prod" in out
    assert "staging" in out


def test_cmd_copy_missing_profile_exits(base_dir):
    with pytest.raises(SystemExit) as exc_info:
        cmd_copy(make_args(base_dir, src="ghost"))
    assert exc_info.value.code == 1


def test_cmd_copy_inherits_src_passphrase_when_dst_omitted(base_dir, capsys):
    _seed(base_dir, "prod", "shared", {"K": "v"})
    cmd_copy(make_args(base_dir, src_passphrase="shared", dst_passphrase=None))
    result = load(profile_path("staging", base_dir=base_dir), "shared")
    assert result["K"] == "v"
