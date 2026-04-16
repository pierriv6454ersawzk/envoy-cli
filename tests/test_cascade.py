import pytest
from pathlib import Path
from envoy.vault import save
from envoy.profile import profile_path
from envoy.cascade import resolve_cascade, cascade_sources, CascadeError


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(name, data, base_dir):
    path = profile_path(name, base_dir=base_dir)
    save(path, data, "pass")


def test_resolve_cascade_single_profile(base_dir):
    _seed("base", {"A": "1", "B": "2"}, base_dir)
    result = resolve_cascade(["base"], "pass", base_dir=base_dir)
    assert result == {"A": "1", "B": "2"}


def test_resolve_cascade_override(base_dir):
    _seed("base", {"A": "1", "B": "2"}, base_dir)
    _seed("prod", {"B": "99", "C": "3"}, base_dir)
    result = resolve_cascade(["base", "prod"], "pass", base_dir=base_dir)
    assert result["A"] == "1"
    assert result["B"] == "99"
    assert result["C"] == "3"


def test_resolve_cascade_three_levels(base_dir):
    _seed("base", {"X": "base", "Y": "base"}, base_dir)
    _seed("mid", {"X": "mid"}, base_dir)
    _seed("top", {"X": "top"}, base_dir)
    result = resolve_cascade(["base", "mid", "top"], "pass", base_dir=base_dir)
    assert result["X"] == "top"
    assert result["Y"] == "base"


def test_resolve_cascade_missing_profile_raises(base_dir):
    with pytest.raises(CascadeError, match="does not exist"):
        resolve_cascade(["ghost"], "pass", base_dir=base_dir)


def test_resolve_cascade_empty_list_raises(base_dir):
    with pytest.raises(CascadeError, match="At least one"):
        resolve_cascade([], "pass", base_dir=base_dir)


def test_cascade_sources_winning_profile(base_dir):
    _seed("base", {"A": "1", "B": "2"}, base_dir)
    _seed("prod", {"B": "99"}, base_dir)
    sources = cascade_sources(["base", "prod"], "pass", base_dir=base_dir)
    assert sources["A"] == ("1", "base")
    assert sources["B"] == ("99", "prod")


def test_cascade_sources_missing_profile_raises(base_dir):
    with pytest.raises(CascadeError):
        cascade_sources(["nope"], "pass", base_dir=base_dir)
