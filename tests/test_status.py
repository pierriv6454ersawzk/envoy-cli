"""Tests for envoy.status and envoy.cli_status."""
import pytest
from unittest.mock import patch, MagicMock

from envoy.status import get_status, format_status, ProfileStatus


DEFAULT_PROFILE = "default"
PASS = "secret"


def _mock_status_deps(exists=True, env=None, locked=False, ttl=None,
                      expired=False, tags=None, schema=None):
    env = env or {"KEY": "val", "OTHER": "x"}
    tags = tags or ["prod"]
    schema = schema or {"KEY": {"required": True}}
    patches = [
        patch("envoy.status.profile_exists", return_value=exists),
        patch("envoy.status.load", return_value=env),
        patch("envoy.status.is_locked", return_value=locked),
        patch("envoy.status.lock_info", return_value={"pid": 1234} if locked else {}),
        patch("envoy.status.get_ttl", return_value=ttl),
        patch("envoy.status.is_profile_expired", return_value=expired),
        patch("envoy.status.list_tags", return_value=tags),
        patch("envoy.status.load_schema", return_value=schema),
        patch("envoy.status.profile_path", return_value="/fake/path"),
    ]
    return patches


def test_get_status_missing_profile():
    with patch("envoy.status.profile_exists", return_value=False):
        s = get_status("ghost", "pass")
    assert not s.exists
    assert s.key_count == 0


def test_get_status_returns_correct_key_count():
    with _mock_status_deps()[0], *_mock_status_deps()[1:]:
        s = get_status(DEFAULT_PROFILE, PASS)
    assert s.key_count == 2


def test_get_status_full():
    ctxs = _mock_status_deps(locked=True, ttl=3600, expired=False, tags=["prod", "v2"])
    with ctxs[0], ctxs[1], ctxs[2], ctxs[3], ctxs[4], ctxs[5], ctxs[6], ctxs[7], ctxs[8]:
        s = get_status(DEFAULT_PROFILE, PASS)
    assert s.exists
    assert s.is_locked
    assert s.lock_owner == 1234
    assert s.ttl_seconds == 3600
    assert "prod" in s.tags
    assert s.schema_keys == 1


def test_format_status_missing():
    s = ProfileStatus(profile="ghost", exists=False)
    out = format_status(s)
    assert "does not exist" in out


def test_format_status_present():
    s = ProfileStatus(
        profile="default", exists=True, key_count=3,
        is_locked=False, ttl_seconds=None, is_expired=False,
        tags=["staging"], schema_keys=2,
    )
    out = format_status(s)
    assert "3" in out
    assert "staging" in out
    assert "2 rule" in out
    assert "no" in out


def test_format_status_expired_shows_yes():
    s = ProfileStatus(
        profile="old", exists=True, key_count=1,
        is_expired=True, tags=[], schema_keys=0,
    )
    out = format_status(s)
    assert "yes" in out
