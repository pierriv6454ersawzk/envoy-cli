"""Tests for envoy.snapshot."""

from __future__ import annotations

import pytest

from envoy.snapshot import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)
from envoy.vault import load, save


PASS = "hunter2"


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(profile: str, env: dict, base_dir: str) -> None:
    save(env, profile, PASS, base_dir=base_dir)


def test_create_snapshot_returns_id(base_dir):
    _seed("dev", {"A": "1"}, base_dir)
    sid = create_snapshot("dev", PASS, base_dir=base_dir)
    assert sid.startswith("dev-")


def test_create_snapshot_appears_in_list(base_dir):
    _seed("dev", {"A": "1"}, base_dir)
    sid = create_snapshot("dev", PASS, base_dir=base_dir)
    entries = list_snapshots(base_dir=base_dir)
    ids = [e["id"] for e in entries]
    assert sid in ids


def test_list_snapshots_filtered_by_profile(base_dir):
    _seed("dev", {"A": "1"}, base_dir)
    _seed("prod", {"B": "2"}, base_dir)
    create_snapshot("dev", PASS, base_dir=base_dir)
    create_snapshot("prod", PASS, base_dir=base_dir)
    dev_snaps = list_snapshots(profile="dev", base_dir=base_dir)
    assert all(e["profile"] == "dev" for e in dev_snaps)
    assert len(dev_snaps) == 1


def test_list_snapshots_empty_when_none(base_dir):
    assert list_snapshots(base_dir=base_dir) == []


def test_snapshot_stores_label(base_dir):
    _seed("dev", {"A": "1"}, base_dir)
    sid = create_snapshot("dev", PASS, label="before-deploy", base_dir=base_dir)
    entry = next(e for e in list_snapshots(base_dir=base_dir) if e["id"] == sid)
    assert entry["label"] == "before-deploy"


def test_restore_snapshot_overwrites_profile(base_dir):
    _seed("dev", {"A": "original"}, base_dir)
    sid = create_snapshot("dev", PASS, base_dir=base_dir)
    # mutate the profile
    save({"A": "changed"}, "dev", PASS, base_dir=base_dir)
    restore_snapshot(sid, PASS, base_dir=base_dir)
    env = load("dev", PASS, base_dir=base_dir)
    assert env["A"] == "original"


def test_restore_snapshot_into_different_profile(base_dir):
    _seed("dev", {"X": "42"}, base_dir)
    sid = create_snapshot("dev", PASS, base_dir=base_dir)
    restore_snapshot(sid, PASS, target_profile="staging", base_dir=base_dir)
    env = load("staging", PASS, base_dir=base_dir)
    assert env["X"] == "42"


def test_restore_missing_snapshot_raises(base_dir):
    with pytest.raises(KeyError):
        restore_snapshot("nonexistent-000", PASS, base_dir=base_dir)


def test_delete_snapshot_removes_entry(base_dir):
    _seed("dev", {"A": "1"}, base_dir)
    sid = create_snapshot("dev", PASS, base_dir=base_dir)
    delete_snapshot(sid, base_dir=base_dir)
    ids = [e["id"] for e in list_snapshots(base_dir=base_dir)]
    assert sid not in ids


def test_delete_missing_snapshot_raises(base_dir):
    with pytest.raises(KeyError):
        delete_snapshot("ghost-000", base_dir=base_dir)
