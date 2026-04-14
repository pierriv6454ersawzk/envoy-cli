"""Tests for envoy.export module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.export import export_env, import_env
from envoy.vault import save, load


PASS = "test-passphrase-42"


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "default.vault"
    save(path, PASS, {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "my app"})
    return path


@pytest.fixture
def dotenv_file(tmp_path: Path) -> Path:
    content = (
        "# Sample env file\n"
        "API_KEY=abc123\n"
        "DEBUG=true\n"
        "GREETING=hello world\n"
        "\n"
        "# trailing comment\n"
    )
    path = tmp_path / ".env"
    path.write_text(content, encoding="utf-8")
    return path


def test_export_returns_string(vault_file: Path) -> None:
    result = export_env(vault_file, PASS)
    assert isinstance(result, str)
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result


def test_export_quotes_values_with_spaces(vault_file: Path) -> None:
    result = export_env(vault_file, PASS)
    assert 'APP_NAME="my app"' in result


def test_export_writes_to_file(vault_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "exported.env"
    export_env(vault_file, PASS, output_path=out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "DB_HOST=localhost" in content


def test_export_wrong_passphrase_raises(vault_file: Path) -> None:
    with pytest.raises(ValueError):
        export_env(vault_file, "wrong-pass")


def test_import_basic(dotenv_file: Path, tmp_path: Path) -> None:
    vault = tmp_path / "new.vault"
    merged = import_env(dotenv_file, vault, PASS)
    assert merged["API_KEY"] == "abc123"
    assert merged["DEBUG"] == "true"
    assert merged["GREETING"] == "hello world"


def test_import_persists_to_vault(dotenv_file: Path, tmp_path: Path) -> None:
    vault = tmp_path / "new.vault"
    import_env(dotenv_file, vault, PASS)
    loaded = load(vault, PASS)
    assert loaded["API_KEY"] == "abc123"


def test_import_no_overwrite_preserves_existing(dotenv_file: Path, tmp_path: Path) -> None:
    vault = tmp_path / "existing.vault"
    save(vault, PASS, {"API_KEY": "original", "EXTRA": "keep"})
    merged = import_env(dotenv_file, vault, PASS, overwrite=False)
    assert merged["API_KEY"] == "original"
    assert merged["EXTRA"] == "keep"
    assert merged["DEBUG"] == "true"


def test_import_overwrite_replaces_existing(dotenv_file: Path, tmp_path: Path) -> None:
    vault = tmp_path / "existing.vault"
    save(vault, PASS, {"API_KEY": "original"})
    merged = import_env(dotenv_file, vault, PASS, overwrite=True)
    assert merged["API_KEY"] == "abc123"


def test_import_missing_source_raises(tmp_path: Path) -> None:
    vault = tmp_path / "new.vault"
    with pytest.raises(FileNotFoundError):
        import_env(tmp_path / "nonexistent.env", vault, PASS)
