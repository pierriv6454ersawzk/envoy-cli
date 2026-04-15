"""Tests for envoy.schema."""

from __future__ import annotations

import pytest

from envoy.schema import (
    SchemaViolation,
    load_schema,
    save_schema,
    validate_env,
)


# ---------------------------------------------------------------------------
# save / load
# ---------------------------------------------------------------------------

def test_save_and_load_schema_roundtrip(tmp_path):
    schema = {"PORT": {"required": True, "type": "integer"}}
    save_schema(str(tmp_path), "default", schema)
    loaded = load_schema(str(tmp_path), "default")
    assert loaded == schema


def test_load_schema_returns_empty_when_missing(tmp_path):
    result = load_schema(str(tmp_path), "nonexistent")
    assert result == {}


def test_save_schema_overwrites_existing(tmp_path):
    save_schema(str(tmp_path), "prod", {"A": {"required": True}})
    save_schema(str(tmp_path), "prod", {"B": {"required": False}})
    loaded = load_schema(str(tmp_path), "prod")
    assert "A" not in loaded
    assert "B" in loaded


# ---------------------------------------------------------------------------
# validate_env
# ---------------------------------------------------------------------------

def test_validate_env_clean_passes():
    schema = {"PORT": {"required": True, "type": "integer"}}
    violations = validate_env({"PORT": "8080"}, schema)
    assert violations == []


def test_validate_env_missing_required_key():
    schema = {"SECRET": {"required": True}}
    violations = validate_env({}, schema)
    assert len(violations) == 1
    assert violations[0].key == "SECRET"
    assert violations[0].severity == "error"


def test_validate_env_missing_optional_key_no_violation():
    schema = {"DEBUG": {"required": False, "type": "boolean"}}
    violations = validate_env({}, schema)
    assert violations == []


def test_validate_env_bad_integer():
    schema = {"PORT": {"type": "integer"}}
    violations = validate_env({"PORT": "not_a_number"}, schema)
    assert len(violations) == 1
    assert "integer" in violations[0].message


def test_validate_env_bad_float():
    schema = {"RATE": {"type": "float"}}
    violations = validate_env({"RATE": "abc"}, schema)
    assert len(violations) == 1


def test_validate_env_valid_boolean_values():
    schema = {"FLAG": {"type": "boolean"}}
    for val in ["true", "false", "1", "0", "yes", "no", "True", "FALSE"]:
        assert validate_env({"FLAG": val}, schema) == []


def test_validate_env_invalid_boolean():
    schema = {"FLAG": {"type": "boolean"}}
    violations = validate_env({"FLAG": "maybe"}, schema)
    assert len(violations) == 1


def test_schema_violation_str_format():
    v = SchemaViolation("MY_KEY", "required key is missing", "error")
    assert "ERROR" in str(v)
    assert "MY_KEY" in str(v)


def test_validate_env_multiple_violations():
    schema = {
        "PORT": {"required": True, "type": "integer"},
        "DEBUG": {"required": True, "type": "boolean"},
    }
    violations = validate_env({"PORT": "bad", "DEBUG": "maybe"}, schema)
    assert len(violations) == 2
