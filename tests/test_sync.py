"""Tests for envoy.sync module."""

import json
import pytest
from pathlib import Path

from envoy.sync import (
    get_remote_config,
    set_remote_config,
    push_profile,
    pull_profile,
    diff_profiles,
    _remote_index_path,
)
from envoy.vault import save
from envoy.profile import profile_path


PASSPHRASE = "sync-secret"


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_set_and_get_remote_config(base_dir):
    config = {"backend": "s3", "bucket": "my-envoy-bucket"}
    set_remote_config(config, base_dir)
    loaded = get_remote_config(base_dir)
    assert loaded == config


def test_get_remote_config_returns_empty_when_missing(base_dir):
    result = get_remote_config(base_dir)
    assert result == {}


def test_push_profile_creates_remote_file(base_dir, tmp_path):
    local = profile_path("prod", base_dir)
    save(str(local), PASSPHRASE, {"KEY": "value"})

    remote = str(tmp_path / "remote" / "prod.env.enc")
    push_profile("prod", PASSPHRASE, remote, base_dir)

    assert Path(remote).exists()


def test_push_profile_missing_raises(base_dir, tmp_path):
    with pytest.raises(FileNotFoundError, match="Profile 'ghost'"):
        push_profile("ghost", PASSPHRASE, str(tmp_path / "out.enc"), base_dir)


def test_pull_profile_restores_data(base_dir, tmp_path):
    remote = str(tmp_path / "remote.enc")
    save(remote, PASSPHRASE, {"REMOTE_KEY": "hello"})

    pull_profile("staging", PASSPHRASE, remote, base_dir)

    dest = profile_path("staging", base_dir)
    assert dest.exists()


def test_pull_profile_missing_remote_raises(base_dir, tmp_path):
    with pytest.raises(FileNotFoundError, match="Remote path"):
        pull_profile("staging", PASSPHRASE, str(tmp_path / "nope.enc"), base_dir)


def test_diff_profiles_detects_changes(base_dir, tmp_path):
    local = profile_path("dev", base_dir)
    save(str(local), PASSPHRASE, {"A": "1", "B": "shared"})

    remote = str(tmp_path / "remote.enc")
    save(remote, PASSPHRASE, {"A": "2", "B": "shared", "C": "new"})

    diff = diff_profiles("dev", PASSPHRASE, remote, base_dir)
    assert "A" in diff
    assert diff["A"] == {"local": "1", "remote": "2"}
    assert "C" in diff
    assert "B" not in diff


def test_diff_profiles_no_diff(base_dir, tmp_path):
    local = profile_path("dev", base_dir)
    save(str(local), PASSPHRASE, {"X": "same"})

    remote = str(tmp_path / "remote.enc")
    save(remote, PASSPHRASE, {"X": "same"})

    diff = diff_profiles("dev", PASSPHRASE, remote, base_dir)
    assert diff == {}
