"""Tests for envoy.archive."""

import pytest
import os
from pathlib import Path
from envoy.archive import create_archive, list_archives, restore_archive, delete_archive
from envoy.vault import save
from envoy.profile import profile_path


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile="default"):
    p = profile_path(base_dir, profile)
    save(p, {"KEY": "value", "FOO": "bar"}, passphrase="pass")


def test_create_archive_returns_path(base_dir):
    _seed(base_dir)
    path = create_archive(base_dir)
    assert path.exists()
    assert path.suffix == ".gz"


def test_create_archive_appears_in_list(base_dir):
    _seed(base_dir)
    create_archive(base_dir, label="test-label")
    entries = list_archives(base_dir)
    assert len(entries) == 1
    assert entries[0]["label"] == "test-label"


def test_list_archives_empty_when_none(base_dir):
    assert list_archives(base_dir) == []


def test_create_multiple_archives(base_dir):
    _seed(base_dir)
    create_archive(base_dir, label="a")
    create_archive(base_dir, label="b")
    entries = list_archives(base_dir)
    assert len(entries) == 2
    labels = [e["label"] for e in entries]
    assert "a" in labels and "b" in labels


def test_restore_archive_recreates_vault(base_dir, tmp_path):
    _seed(base_dir)
    archive_path = create_archive(base_dir)
    # Remove vault files
    from envoy.profile import get_vault_dir
    import shutil
    vault_dir = get_vault_dir(base_dir)
    shutil.rmtree(vault_dir)
    assert not Path(vault_dir).exists() or not list(Path(vault_dir).glob("*.vault"))
    restore_archive(base_dir, archive_path.name)
    assert Path(profile_path(base_dir, "default")).exists()


def test_restore_missing_archive_raises(base_dir):
    with pytest.raises(FileNotFoundError):
        restore_archive(base_dir, "nonexistent.tar.gz")


def test_delete_archive_removes_file(base_dir):
    _seed(base_dir)
    path = create_archive(base_dir)
    result = delete_archive(base_dir, path.name)
    assert result is True
    assert not path.exists()
    assert list_archives(base_dir) == []


def test_delete_missing_archive_returns_false(base_dir):
    result = delete_archive(base_dir, "ghost.tar.gz")
    assert result is False
