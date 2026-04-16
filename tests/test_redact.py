"""Tests for envoy.redact module."""

import pytest
from envoy.redact import is_sensitive, redact_env, redact_value, MASK, DEFAULT_PATTERNS


def test_is_sensitive_password():
    assert is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_token():
    assert is_sensitive("GITHUB_TOKEN") is True


def test_is_sensitive_api_key():
    assert is_sensitive("STRIPE_API_KEY") is True


def test_is_sensitive_non_sensitive():
    assert is_sensitive("APP_PORT") is False
    assert is_sensitive("DEBUG") is False


def test_is_sensitive_custom_pattern():
    assert is_sensitive("MY_INTERNAL_VAR", patterns=[r"(?i)internal"]) is True


def test_redact_env_masks_sensitive_keys():
    env = {"DB_PASSWORD": "s3cr3t", "APP_PORT": "8080"}
    result = redact_env(env)
    assert result["DB_PASSWORD"] == MASK
    assert result["APP_PORT"] == "8080"


def test_redact_env_does_not_mutate_original():
    env = {"DB_PASSWORD": "s3cr3t"}
    result = redact_env(env)
    assert env["DB_PASSWORD"] == "s3cr3t"
    assert result["DB_PASSWORD"] == MASK


def test_redact_env_reveal_returns_plain():
    env = {"DB_PASSWORD": "s3cr3t", "APP_PORT": "8080"}
    result = redact_env(env, reveal=True)
    assert result["DB_PASSWORD"] == "s3cr3t"
    assert result["APP_PORT"] == "8080"


def test_redact_env_custom_patterns():
    env = {"MY_CUSTOM_THING": "hidden", "APP_PORT": "8080"}
    result = redact_env(env, patterns=[r"(?i)custom"])
    assert result["MY_CUSTOM_THING"] == MASK
    assert result["APP_PORT"] == "8080"


def test_redact_value_sensitive():
    assert redact_value("AUTH_TOKEN", "abc123") == MASK


def test_redact_value_non_sensitive():
    assert redact_value("HOST", "localhost") == "localhost"


def test_redact_value_reveal():
    assert redact_value("AUTH_TOKEN", "abc123", reveal=True) == "abc123"


def test_redact_env_empty():
    assert redact_env({}) == {}
