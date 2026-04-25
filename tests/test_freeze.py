"""Tests for envoy.freeze."""

from __future__ import annotations

import pytest

from envoy.freeze import (
    FreezeError,
    assert_not_frozen,
    freeze_profile,
    is_frozen,
    list_frozen,
    unfreeze_profile,
)
from envoy.vault import save


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir: str, profile: str = "default") -> None:
    save({"KEY": "value"}, profile, "pass", base_dir)


def test_is_frozen_returns_false_when_missing(base_dir):
    _seed(base_dir)
    assert is_frozen("default", base_dir) is False


def test_freeze_profile_marks_as_frozen(base_dir):
    _seed(base_dir)
    freeze_profile("default", base_dir)
    assert is_frozen("default", base_dir) is True


def test_freeze_profile_missing_profile_raises(base_dir):
    with pytest.raises(FreezeError, match="does not exist"):
        freeze_profile("ghost", base_dir)


def test_unfreeze_profile_removes_frozen_mark(base_dir):
    _seed(base_dir)
    freeze_profile("default", base_dir)
    unfreeze_profile("default", base_dir)
    assert is_frozen("default", base_dir) is False


def test_unfreeze_profile_idempotent(base_dir):
    _seed(base_dir)
    # Should not raise even if profile was never frozen
    unfreeze_profile("default", base_dir)
    assert is_frozen("default", base_dir) is False


def test_list_frozen_empty_when_none(base_dir):
    _seed(base_dir)
    assert list_frozen(base_dir) == []


def test_list_frozen_returns_frozen_profiles(base_dir):
    for name in ("alpha", "beta", "gamma"):
        _seed(base_dir, name)
    freeze_profile("alpha", base_dir)
    freeze_profile("gamma", base_dir)
    assert list_frozen(base_dir) == ["alpha", "gamma"]


def test_list_frozen_excludes_unfrozen_profiles(base_dir):
    for name in ("alpha", "beta"):
        _seed(base_dir, name)
    freeze_profile("alpha", base_dir)
    freeze_profile("beta", base_dir)
    unfreeze_profile("beta", base_dir)
    assert list_frozen(base_dir) == ["alpha"]


def test_assert_not_frozen_passes_when_unfrozen(base_dir):
    _seed(base_dir)
    # Should not raise
    assert_not_frozen("default", base_dir)


def test_assert_not_frozen_raises_when_frozen(base_dir):
    _seed(base_dir)
    freeze_profile("default", base_dir)
    with pytest.raises(FreezeError, match="frozen"):
        assert_not_frozen("default", base_dir)
