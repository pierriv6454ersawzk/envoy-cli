"""Tests for envoy.trust module."""

import pytest

from envoy.trust import (
    TrustError,
    get_trust_record,
    is_trusted,
    list_trusted,
    revoke_trust,
    trust_profile,
)
from envoy.vault import save


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(profile: str, base_dir: str) -> None:
    save({"KEY": "value"}, profile, "pass", base_dir=base_dir)


def test_is_trusted_returns_false_when_missing(base_dir):
    _seed("dev", base_dir)
    assert is_trusted("dev", base_dir=base_dir) is False


def test_trust_profile_marks_as_trusted(base_dir):
    _seed("dev", base_dir)
    trust_profile("dev", base_dir=base_dir)
    assert is_trusted("dev", base_dir=base_dir) is True


def test_trust_profile_stores_reason(base_dir):
    _seed("dev", base_dir)
    trust_profile("dev", reason="reviewed by alice", base_dir=base_dir)
    record = get_trust_record("dev", base_dir=base_dir)
    assert record["reason"] == "reviewed by alice"


def test_trust_profile_stores_timestamp(base_dir):
    _seed("dev", base_dir)
    trust_profile("dev", base_dir=base_dir)
    record = get_trust_record("dev", base_dir=base_dir)
    assert isinstance(record["timestamp"], float)
    assert record["timestamp"] > 0


def test_trust_profile_missing_profile_raises(base_dir):
    with pytest.raises(TrustError, match="does not exist"):
        trust_profile("ghost", base_dir=base_dir)


def test_trust_profile_overwrites_existing(base_dir):
    _seed("dev", base_dir)
    trust_profile("dev", reason="first", base_dir=base_dir)
    trust_profile("dev", reason="second", base_dir=base_dir)
    record = get_trust_record("dev", base_dir=base_dir)
    assert record["reason"] == "second"


def test_revoke_trust_removes_record(base_dir):
    _seed("dev", base_dir)
    trust_profile("dev", base_dir=base_dir)
    revoke_trust("dev", base_dir=base_dir)
    assert is_trusted("dev", base_dir=base_dir) is False
    assert get_trust_record("dev", base_dir=base_dir) is None


def test_revoke_trust_missing_record_raises(base_dir):
    _seed("dev", base_dir)
    with pytest.raises(TrustError, match="no trust record"):
        revoke_trust("dev", base_dir=base_dir)


def test_list_trusted_empty_when_none(base_dir):
    assert list_trusted(base_dir=base_dir) == []


def test_list_trusted_returns_trusted_profiles(base_dir):
    _seed("dev", base_dir)
    _seed("prod", base_dir)
    _seed("staging", base_dir)
    trust_profile("dev", base_dir=base_dir)
    trust_profile("prod", base_dir=base_dir)
    trusted = list_trusted(base_dir=base_dir)
    assert sorted(trusted) == ["dev", "prod"]
    assert "staging" not in trusted


def test_get_trust_record_returns_none_when_missing(base_dir):
    _seed("dev", base_dir)
    assert get_trust_record("dev", base_dir=base_dir) is None
