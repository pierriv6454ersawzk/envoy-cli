"""Tests for envoy.cli_schema CLI commands."""

from __future__ import annotations

import argparse
import json
import sys

import pytest

from envoy.cli_schema import cmd_schema_set, cmd_schema_show, cmd_schema_validate
from envoy.profile import get_vault_dir
from envoy.schema import load_schema
from envoy.vault import save as vault_save


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def make_args(base_dir, profile="default", **kwargs):
    ns = argparse.Namespace(base_dir=base_dir, profile=profile, **kwargs)
    return ns


def _seed(base_dir, profile="default", passphrase="pass"):
    vault_dir = get_vault_dir(base_dir)
    vault_save(vault_dir, profile, passphrase, {"PORT": "8080", "DEBUG": "true"})


# ---------------------------------------------------------------------------
# cmd_schema_set
# ---------------------------------------------------------------------------

def test_cmd_schema_set_creates_rule(base_dir, capsys):
    args = make_args(base_dir, key="PORT", rules=["required=true", "type=integer"])
    cmd_schema_set(args)
    schema = load_schema(get_vault_dir(base_dir), "default")
    assert schema["PORT"]["required"] is True
    assert schema["PORT"]["type"] == "integer"


def test_cmd_schema_set_invalid_type_exits(base_dir):
    args = make_args(base_dir, key="X", rules=["type=uuid"])
    with pytest.raises(SystemExit):
        cmd_schema_set(args)


def test_cmd_schema_set_invalid_rule_format_exits(base_dir):
    args = make_args(base_dir, key="X", rules=["badformat"])
    with pytest.raises(SystemExit):
        cmd_schema_set(args)


# ---------------------------------------------------------------------------
# cmd_schema_show
# ---------------------------------------------------------------------------

def test_cmd_schema_show_empty(base_dir, capsys):
    args = make_args(base_dir)
    cmd_schema_show(args)
    out = capsys.readouterr().out
    assert "No schema" in out


def test_cmd_schema_show_displays_json(base_dir, capsys):
    args_set = make_args(base_dir, key="PORT", rules=["type=integer"])
    cmd_schema_set(args_set)
    cmd_schema_show(make_args(base_dir))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "PORT" in data


# ---------------------------------------------------------------------------
# cmd_schema_validate
# ---------------------------------------------------------------------------

def test_cmd_schema_validate_no_schema(base_dir, capsys):
    _seed(base_dir)
    args = make_args(base_dir, passphrase="pass")
    cmd_schema_validate(args)  # should not raise
    out = capsys.readouterr().out
    assert "Nothing to validate" in out


def test_cmd_schema_validate_passes(base_dir, capsys):
    _seed(base_dir)
    set_args = make_args(base_dir, key="PORT", rules=["required=true", "type=integer"])
    cmd_schema_set(set_args)
    val_args = make_args(base_dir, passphrase="pass")
    cmd_schema_validate(val_args)
    out = capsys.readouterr().out
    assert "valid" in out


def test_cmd_schema_validate_fails_exits(base_dir):
    _seed(base_dir)
    set_args = make_args(base_dir, key="MISSING_KEY", rules=["required=true"])
    cmd_schema_set(set_args)
    val_args = make_args(base_dir, passphrase="pass")
    with pytest.raises(SystemExit) as exc:
        cmd_schema_validate(val_args)
    assert exc.value.code == 1


def test_cmd_schema_validate_missing_profile_exits(base_dir):
    args = make_args(base_dir, profile="ghost", passphrase="pass")
    with pytest.raises(SystemExit):
        cmd_schema_validate(args)
