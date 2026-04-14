"""Tests for the envoy CLI commands."""

import pytest
from unittest.mock import patch, MagicMock
from argparse import Namespace

from envoy.cli import cmd_set, cmd_get, cmd_list, build_parser


PASSPHRASE = "test-passphrase"


@pytest.fixture
def vault_file(tmp_path):
    return str(tmp_path / ".env.vault")


def make_args(file, **kwargs):
    return Namespace(file=file, **kwargs)


@patch("envoy.cli.getpass", return_value=PASSPHRASE)
def test_cmd_set_creates_new_vault(mock_getpass, vault_file):
    args = make_args(vault_file, pairs=["FOO=bar", "BAZ=qux"])
    cmd_set(args)

    # Verify by loading directly
    from envoy.vault import load
    env = load(vault_file, PASSPHRASE)
    assert env["FOO"] == "bar"
    assert env["BAZ"] == "qux"


@patch("envoy.cli.getpass", return_value=PASSPHRASE)
def test_cmd_set_updates_existing_vault(mock_getpass, vault_file):
    from envoy.vault import save
    save(vault_file, {"EXISTING": "value"}, PASSPHRASE)

    args = make_args(vault_file, pairs=["NEW=entry"])
    cmd_set(args)

    from envoy.vault import load
    env = load(vault_file, PASSPHRASE)
    assert env["EXISTING"] == "value"
    assert env["NEW"] == "entry"


@patch("envoy.cli.getpass", return_value=PASSPHRASE)
def test_cmd_set_invalid_pair_exits(mock_getpass, vault_file):
    args = make_args(vault_file, pairs=["NOEQUALSSIGN"])
    with pytest.raises(SystemExit) as exc_info:
        cmd_set(args)
    assert exc_info.value.code == 1


@patch("envoy.cli.getpass", return_value=PASSPHRASE)
def test_cmd_get_returns_value(mock_getpass, vault_file, capsys):
    from envoy.vault import save
    save(vault_file, {"MY_KEY": "my_value"}, PASSPHRASE)

    args = make_args(vault_file, key="MY_KEY")
    cmd_get(args)

    captured = capsys.readouterr()
    assert captured.out.strip() == "my_value"


@patch("envoy.cli.getpass", return_value=PASSPHRASE)
def test_cmd_get_missing_key_exits(mock_getpass, vault_file):
    from envoy.vault import save
    save(vault_file, {"OTHER": "val"}, PASSPHRASE)

    args = make_args(vault_file, key="MISSING")
    with pytest.raises(SystemExit) as exc_info:
        cmd_get(args)
    assert exc_info.value.code == 1


@patch("envoy.cli.getpass", return_value=PASSPHRASE)
def test_cmd_get_missing_file_exits(mock_getpass, vault_file):
    args = make_args(vault_file, key="ANY")
    with pytest.raises(SystemExit) as exc_info:
        cmd_get(args)
    assert exc_info.value.code == 1


@patch("envoy.cli.getpass", return_value=PASSPHRASE)
def test_cmd_list_prints_all_keys(mock_getpass, vault_file, capsys):
    from envoy.vault import save
    save(vault_file, {"ALPHA": "1", "BETA": "2"}, PASSPHRASE)

    args = make_args(vault_file)
    cmd_list(args)

    captured = capsys.readouterr()
    assert "ALPHA=1" in captured.out
    assert "BETA=2" in captured.out


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser.prog == "envoy"
