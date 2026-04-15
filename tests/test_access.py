"""Unit tests for envoy.access."""

from __future__ import annotations

import pytest

from envoy.access import (
    all_grants,
    grant_access,
    has_access,
    list_access,
    revoke_access,
)


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def test_grant_access_creates_entry(base_dir):
    grant_access("production", "alice", base_dir=base_dir)
    assert has_access("production", "alice", base_dir=base_dir)


def test_list_access_returns_empty_when_missing(base_dir):
    assert list_access("staging", base_dir=base_dir) == []


def test_grant_access_idempotent(base_dir):
    grant_access("production", "alice", base_dir=base_dir)
    grant_access("production", "alice", base_dir=base_dir)
    assert list_access("production", base_dir=base_dir).count("alice") == 1


def test_grant_multiple_labels(base_dir):
    grant_access("production", "alice", base_dir=base_dir)
    grant_access("production", "bob", base_dir=base_dir)
    labels = list_access("production", base_dir=base_dir)
    assert "alice" in labels
    assert "bob" in labels


def test_revoke_removes_label(base_dir):
    grant_access("production", "alice", base_dir=base_dir)
    revoke_access("production", "alice", base_dir=base_dir)
    assert not has_access("production", "alice", base_dir=base_dir)


def test_revoke_missing_label_is_silent(base_dir):
    revoke_access("production", "ghost", base_dir=base_dir)  # should not raise


def test_revoke_last_label_removes_profile_entry(base_dir):
    grant_access("staging", "carol", base_dir=base_dir)
    revoke_access("staging", "carol", base_dir=base_dir)
    grants = all_grants(base_dir=base_dir)
    assert "staging" not in grants


def test_all_grants_returns_full_mapping(base_dir):
    grant_access("prod", "alice", base_dir=base_dir)
    grant_access("dev", "bob", base_dir=base_dir)
    grants = all_grants(base_dir=base_dir)
    assert "prod" in grants
    assert "dev" in grants


def test_has_access_returns_false_for_unknown_label(base_dir):
    grant_access("prod", "alice", base_dir=base_dir)
    assert not has_access("prod", "dave", base_dir=base_dir)
