"""Tests for envoy.score and envoy.cli_score."""

from __future__ import annotations

import pytest

from envoy.vault import save
from envoy.schema import save_schema
from envoy.score import score_profile, ScoreReport
from envoy.cli_score import cmd_score


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile="default", passphrase="pw", env=None):
    env = env or {"API_KEY": "abc", "DB_HOST": "localhost"}
    save(profile, env, passphrase, base_dir=base_dir)
    return env


# ---------------------------------------------------------------------------
# score_profile
# ---------------------------------------------------------------------------

def test_score_returns_report(base_dir):
    _seed(base_dir)
    report = score_profile("default", "pw", base_dir=base_dir)
    assert isinstance(report, ScoreReport)
    assert report.profile == "default"
    assert report.total_keys == 2


def test_score_no_schema_gives_full_coverage(base_dir):
    _seed(base_dir)
    report = score_profile("default", "pw", base_dir=base_dir)
    assert report.schema_coverage == 1.0


def test_score_partial_schema_coverage(base_dir):
    _seed(base_dir, env={"API_KEY": "x"})
    save_schema("default", {
        "API_KEY": {"type": "str", "required": True},
        "MISSING_KEY": {"type": "str", "required": True},
    }, base_dir=base_dir)
    report = score_profile("default", "pw", base_dir=base_dir)
    assert report.schema_coverage == 0.5
    assert report.score < 100


def test_score_full_schema_coverage(base_dir):
    _seed(base_dir, env={"API_KEY": "x", "DB_HOST": "h"})
    save_schema("default", {
        "API_KEY": {"type": "str", "required": True},
        "DB_HOST": {"type": "str", "required": True},
    }, base_dir=base_dir)
    report = score_profile("default", "pw", base_dir=base_dir)
    assert report.schema_coverage == 1.0


def test_score_grade_a_for_perfect(base_dir):
    _seed(base_dir, env={"API_KEY": "x"})
    report = score_profile("default", "pw", base_dir=base_dir)
    assert report.grade == "A"
    assert report.score == 100


def test_score_missing_profile_raises(base_dir):
    with pytest.raises(ValueError, match="does not exist"):
        score_profile("nonexistent", "pw", base_dir=base_dir)


def test_score_as_dict_has_expected_keys(base_dir):
    _seed(base_dir)
    d = score_profile("default", "pw", base_dir=base_dir).as_dict()
    for key in ("profile", "total_keys", "schema_coverage", "lint_errors", "lint_warnings", "score", "grade"):
        assert key in d


# ---------------------------------------------------------------------------
# cmd_score
# ---------------------------------------------------------------------------

class _Args:
    def __init__(self, profile, passphrase, base_dir):
        self.profile = profile
        self.passphrase = passphrase
        self.base_dir = base_dir


def test_cmd_score_prints_output(base_dir, capsys):
    _seed(base_dir)
    cmd_score(_Args("default", "pw", base_dir))
    out = capsys.readouterr().out
    assert "Score" in out
    assert "100" in out


def test_cmd_score_missing_profile_exits(base_dir):
    with pytest.raises(SystemExit):
        cmd_score(_Args("ghost", "pw", base_dir))
