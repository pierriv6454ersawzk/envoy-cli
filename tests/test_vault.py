"""Unit tests for envoy.vault."""

import pytest
from pathlib import Path
from envoy.vault import save, load, _parse_env, _serialize_env


PASSPHRASE = "vault-passphrase-123"
SAMPLE_ENV = {"API_KEY": "abc123", "DEBUG": "true", "PORT": "8080"}


def test_parse_env_basic():
    text = "KEY=value\nOTHER=123\n"
    assert _parse_env(text) == {"KEY": "value", "OTHER": "123"}


def test_parse_env_ignores_comments_and_blanks():
    text = "# comment\n\nKEY=val\n"
    assert _parse_env(text) == {"KEY": "val"}


def test_serialize_env_roundtrip():
    serialized = _serialize_env(SAMPLE_ENV)
    parsed = _parse_env(serialized)
    assert parsed == SAMPLE_ENV


def test_save_and_load_roundtrip(tmp_path: Path):
    vault_file = tmp_path / "test.vault"
    save(SAMPLE_ENV, vault_file, PASSPHRASE)
    assert vault_file.exists()
    loaded = load(vault_file, PASSPHRASE)
    assert loaded == SAMPLE_ENV


def test_load_wrong_passphrase_raises(tmp_path: Path):
    vault_file = tmp_path / "test.vault"
    save(SAMPLE_ENV, vault_file, PASSPHRASE)
    with pytest.raises(ValueError):
        load(vault_file, "bad-passphrase")


def test_load_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load(tmp_path / "nonexistent.vault", PASSPHRASE)
