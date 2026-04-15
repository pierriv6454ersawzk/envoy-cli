"""Tests for CLI import/export commands."""

import argparse
import pytest
from pathlib import Path
from envoy.import_export_cli import cmd_export, cmd_import
from envoy.vault import save


@pytest.fixture()
def base_dir(tmp_path: Path) -> Path:
    return tmp_path


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "base_dir": None,
        "profile": "default",
        "passphrase": "secret",
        "output": None,
        "mask": False,
        "input": None,
        "overwrite": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _seed(base_dir: Path, profile: str = "default", passphrase: str = "secret") -> None:
    from envoy.profile import profile_path, get_vault_dir
    vault_dir = get_vault_dir(base_dir)
    path = profile_path(vault_dir, profile)
    save(path, {"APP_ENV": "production", "DB_URL": "postgres://localhost/db"}, passphrase)


def test_cmd_export_prints_to_stdout(base_dir, capsys):
    _seed(base_dir)
    args = make_args(base_dir=base_dir)
    cmd_export(args)
    captured = capsys.readouterr()
    assert "APP_ENV" in captured.out
    assert "DB_URL" in captured.out


def test_cmd_export_writes_to_file(base_dir, tmp_path):
    _seed(base_dir)
    out_file = tmp_path / "out.env"
    args = make_args(base_dir=base_dir, output=str(out_file))
    cmd_export(args)
    content = out_file.read_text()
    assert "APP_ENV" in content


def test_cmd_export_missing_profile_exits(base_dir):
    args = make_args(base_dir=base_dir, profile="nonexistent")
    with pytest.raises(SystemExit) as exc_info:
        cmd_export(args)
    assert exc_info.value.code == 1


def test_cmd_export_wrong_passphrase_exits(base_dir):
    _seed(base_dir)
    args = make_args(base_dir=base_dir, passphrase="wrong")
    with pytest.raises(SystemExit) as exc_info:
        cmd_export(args)
    assert exc_info.value.code == 1


def test_cmd_import_creates_profile(base_dir, tmp_path):
    env_file = tmp_path / "import.env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    args = make_args(base_dir=base_dir, input=str(env_file))
    cmd_import(args)

    from envoy.profile import profile_path, get_vault_dir
    from envoy.vault import load
    vault_dir = get_vault_dir(base_dir)
    path = profile_path(vault_dir, "default")
    data = load(path, "secret")
    assert data["FOO"] == "bar"
    assert data["BAZ"] == "qux"


def test_cmd_import_missing_file_exits(base_dir):
    args = make_args(base_dir=base_dir, input="/nonexistent/file.env")
    with pytest.raises(SystemExit) as exc_info:
        cmd_import(args)
    assert exc_info.value.code == 1


def test_cmd_import_reports_count(base_dir, tmp_path, capsys):
    env_file = tmp_path / "vars.env"
    env_file.write_text("KEY1=val1\nKEY2=val2\nKEY3=val3\n")
    args = make_args(base_dir=base_dir, input=str(env_file))
    cmd_import(args)
    captured = capsys.readouterr()
    assert "3" in captured.out
