"""Tests for envoy.label"""
import pytest
from pathlib import Path
from envoy.label import add_label, remove_label, list_labels, find_by_label, all_labels, LabelError
from envoy.vault import save


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile="default", passphrase="pass"):
    save({"KEY": "val"}, profile, passphrase, base_dir=base_dir)


def test_add_label_creates_entry(base_dir):
    _seed(base_dir)
    add_label("default", "production", base_dir)
    assert "production" in list_labels("default", base_dir)


def test_add_label_idempotent(base_dir):
    _seed(base_dir)
    add_label("default", "staging", base_dir)
    add_label("default", "staging", base_dir)
    assert list_labels("default", base_dir).count("staging") == 1


def test_add_multiple_labels(base_dir):
    _seed(base_dir)
    add_label("default", "alpha", base_dir)
    add_label("default", "beta", base_dir)
    labels = list_labels("default", base_dir)
    assert "alpha" in labels
    assert "beta" in labels


def test_add_label_missing_profile_raises(base_dir):
    with pytest.raises(LabelError, match="does not exist"):
        add_label("ghost", "x", base_dir)


def test_add_label_empty_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(LabelError, match="empty"):
        add_label("default", "  ", base_dir)


def test_remove_label(base_dir):
    _seed(base_dir)
    add_label("default", "remove-me", base_dir)
    remove_label("default", "remove-me", base_dir)
    assert "remove-me" not in list_labels("default", base_dir)


def test_remove_missing_label_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(LabelError, match="not found"):
        remove_label("default", "nope", base_dir)


def test_find_by_label(base_dir):
    _seed(base_dir, "default")
    _seed(base_dir, "prod")
    add_label("default", "shared", base_dir)
    add_label("prod", "shared", base_dir)
    results = find_by_label("shared", base_dir)
    assert "default" in results
    assert "prod" in results


def test_find_by_label_no_match(base_dir):
    _seed(base_dir)
    assert find_by_label("nonexistent", base_dir) == []


def test_all_labels_returns_full_index(base_dir):
    _seed(base_dir, "default")
    _seed(base_dir, "dev")
    add_label("default", "x", base_dir)
    add_label("dev", "y", base_dir)
    index = all_labels(base_dir)
    assert index["default"] == ["x"]
    assert index["dev"] == ["y"]
