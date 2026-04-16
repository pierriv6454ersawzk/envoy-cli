"""Tests for envoy.compare module."""
import pytest
from pathlib import Path
from envoy.vault import save
from envoy.compare import compare_profiles, format_compare


@pytest.fixture
def base_dir(tmp_path: Path) -> Path:
    return tmp_path


def _seed(path: str, passphrase: str, data: dict) -> None:
    save(path, passphrase, data)


def test_compare_identical_profiles(base_dir):
    a = str(base_dir / "a.env")
    b = str(base_dir / "b.env")
    _seed(a, "pass", {"KEY": "value"})
    _seed(b, "pass", {"KEY": "value"})
    result = compare_profiles(a, "pass", b, "pass")
    assert result.is_identical
    assert result.in_both_same == {"KEY": "value"}


def test_compare_detects_only_in_a(base_dir):
    a = str(base_dir / "a.env")
    b = str(base_dir / "b.env")
    _seed(a, "pass", {"ONLY_A": "1", "SHARED": "x"})
    _seed(b, "pass", {"SHARED": "x"})
    result = compare_profiles(a, "pass", b, "pass")
    assert "ONLY_A" in result.only_in_a
    assert not result.only_in_b
    assert not result.is_identical


def test_compare_detects_only_in_b(base_dir):
    a = str(base_dir / "a.env")
    b = str(base_dir / "b.env")
    _seed(a, "pass", {"SHARED": "x"})
    _seed(b, "pass", {"ONLY_B": "2", "SHARED": "x"})
    result = compare_profiles(a, "pass", b, "pass")
    assert "ONLY_B" in result.only_in_b
    assert not result.only_in_a


def test_compare_detects_differing_values(base_dir):
    a = str(base_dir / "a.env")
    b = str(base_dir / "b.env")
    _seed(a, "pass", {"KEY": "old"})
    _seed(b, "pass", {"KEY": "new"})
    result = compare_profiles(a, "pass", b, "pass")
    assert "KEY" in result.in_both_different
    assert result.in_both_different["KEY"] == ("old", "new")


def test_format_compare_masks_values(base_dir):
    a = str(base_dir / "a.env")
    b = str(base_dir / "b.env")
    _seed(a, "pass", {"SECRET": "hunter2"})
    _seed(b, "pass", {})
    result = compare_profiles(a, "pass", b, "pass")
    output = format_compare(result, mask=True)
    assert "hunter2" not in output
    assert "***" in output


def test_format_compare_reveals_values_when_requested(base_dir):
    a = str(base_dir / "a.env")
    b = str(base_dir / "b.env")
    _seed(a, "pass", {"SECRET": "hunter2"})
    _seed(b, "pass", {})
    result = compare_profiles(a, "pass", b, "pass")
    output = format_compare(result, mask=False)
    assert "hunter2" in output


def test_format_compare_identical_message(base_dir):
    a = str(base_dir / "a.env")
    b = str(base_dir / "b.env")
    _seed(a, "pass", {"K": "v"})
    _seed(b, "pass", {"K": "v"})
    result = compare_profiles(a, "pass", b, "pass")
    assert format_compare(result) == "Profiles are identical."


def test_wrong_passphrase_raises(base_dir):
    a = str(base_dir / "a.env")
    b = str(base_dir / "b.env")
    _seed(a, "correct", {"K": "v"})
    _seed(b, "correct", {"K": "v"})
    with pytest.raises(ValueError):
        compare_profiles(a, "wrong", b, "correct")
