"""Tests for envoy.endorsement."""

from __future__ import annotations

import pytest

from envoy.endorsement import (
    EndorsementError,
    all_endorsements,
    endorse_profile,
    is_endorsed_by,
    list_endorsements,
    revoke_endorsement,
)
from envoy.vault import save


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir: str, profile: str = "default") -> None:
    save({"KEY": "value"}, profile, "pass", base_dir=base_dir)


def test_endorse_profile_creates_entry(base_dir):
    _seed(base_dir)
    entry = endorse_profile("default", "alice", base_dir=base_dir)
    assert entry["reviewer"] == "alice"
    assert "timestamp" in entry


def test_endorse_profile_with_note(base_dir):
    _seed(base_dir)
    entry = endorse_profile("default", "bob", note="LGTM", base_dir=base_dir)
    assert entry["note"] == "LGTM"


def test_endorse_missing_profile_raises(base_dir):
    with pytest.raises(EndorsementError, match="does not exist"):
        endorse_profile("ghost", "alice", base_dir=base_dir)


def test_endorse_empty_reviewer_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(EndorsementError, match="empty"):
        endorse_profile("default", "  ", base_dir=base_dir)


def test_list_endorsements_empty_when_none(base_dir):
    _seed(base_dir)
    assert list_endorsements("default", base_dir=base_dir) == []


def test_list_endorsements_returns_all(base_dir):
    _seed(base_dir)
    endorse_profile("default", "alice", base_dir=base_dir)
    endorse_profile("default", "bob", base_dir=base_dir)
    entries = list_endorsements("default", base_dir=base_dir)
    assert len(entries) == 2
    reviewers = {e["reviewer"] for e in entries}
    assert reviewers == {"alice", "bob"}


def test_is_endorsed_by_true(base_dir):
    _seed(base_dir)
    endorse_profile("default", "alice", base_dir=base_dir)
    assert is_endorsed_by("default", "alice", base_dir=base_dir) is True


def test_is_endorsed_by_false(base_dir):
    _seed(base_dir)
    assert is_endorsed_by("default", "alice", base_dir=base_dir) is False


def test_revoke_endorsement_removes_reviewer(base_dir):
    _seed(base_dir)
    endorse_profile("default", "alice", base_dir=base_dir)
    endorse_profile("default", "bob", base_dir=base_dir)
    removed = revoke_endorsement("default", "alice", base_dir=base_dir)
    assert removed is True
    assert not is_endorsed_by("default", "alice", base_dir=base_dir)
    assert is_endorsed_by("default", "bob", base_dir=base_dir)


def test_revoke_endorsement_returns_false_when_not_present(base_dir):
    _seed(base_dir)
    assert revoke_endorsement("default", "nobody", base_dir=base_dir) is False


def test_all_endorsements_returns_full_index(base_dir):
    _seed(base_dir)
    save({"X": "1"}, "staging", "pass", base_dir=base_dir)
    endorse_profile("default", "alice", base_dir=base_dir)
    endorse_profile("staging", "bob", base_dir=base_dir)
    index = all_endorsements(base_dir=base_dir)
    assert "default" in index
    assert "staging" in index


def test_all_endorsements_empty_when_none(base_dir):
    assert all_endorsements(base_dir=base_dir) == {}
