"""Tests for envoy.pipeline."""

from __future__ import annotations

import pytest

from envoy.pipeline import (
    PipelineError,
    delete_pipeline,
    list_pipelines,
    load_pipeline,
    save_pipeline,
)
from envoy.vault import save as vault_save


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir: str, profile: str = "default") -> None:
    vault_save({"KEY": "val"}, profile, "pass", base_dir=base_dir)


def _steps():
    return [{"action": "lint"}, {"action": "snapshot"}]


def test_save_and_list_pipeline(base_dir):
    _seed(base_dir)
    save_pipeline("deploy", "default", _steps(), base_dir=base_dir)
    assert "deploy" in list_pipelines(base_dir=base_dir)


def test_load_pipeline_returns_steps(base_dir):
    _seed(base_dir)
    save_pipeline("ci", "default", _steps(), base_dir=base_dir)
    result = load_pipeline("ci", base_dir=base_dir)
    assert result["profile"] == "default"
    assert len(result["steps"]) == 2
    assert result["steps"][0]["action"] == "lint"


def test_list_pipelines_empty_when_none(base_dir):
    assert list_pipelines(base_dir=base_dir) == []


def test_load_missing_pipeline_raises(base_dir):
    with pytest.raises(PipelineError, match="not found"):
        load_pipeline("ghost", base_dir=base_dir)


def test_save_pipeline_empty_steps_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(PipelineError, match="at least one step"):
        save_pipeline("bad", "default", [], base_dir=base_dir)


def test_save_pipeline_invalid_action_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(PipelineError, match="Unknown step action"):
        save_pipeline("bad", "default", [{"action": "fly"}], base_dir=base_dir)


def test_save_pipeline_missing_profile_raises(base_dir):
    with pytest.raises(PipelineError, match="does not exist"):
        save_pipeline("p", "no-such-profile", _steps(), base_dir=base_dir)


def test_delete_pipeline_removes_entry(base_dir):
    _seed(base_dir)
    save_pipeline("temp", "default", _steps(), base_dir=base_dir)
    delete_pipeline("temp", base_dir=base_dir)
    assert "temp" not in list_pipelines(base_dir=base_dir)


def test_delete_missing_pipeline_raises(base_dir):
    with pytest.raises(PipelineError, match="not found"):
        delete_pipeline("ghost", base_dir=base_dir)


def test_save_pipeline_overwrites_existing(base_dir):
    _seed(base_dir)
    save_pipeline("p", "default", _steps(), base_dir=base_dir)
    new_steps = [{"action": "export"}]
    save_pipeline("p", "default", new_steps, base_dir=base_dir)
    result = load_pipeline("p", base_dir=base_dir)
    assert len(result["steps"]) == 1
    assert result["steps"][0]["action"] == "export"


def test_list_pipelines_sorted(base_dir):
    _seed(base_dir)
    for name in ["zebra", "alpha", "mango"]:
        save_pipeline(name, "default", _steps(), base_dir=base_dir)
    assert list_pipelines(base_dir=base_dir) == ["alpha", "mango", "zebra"]
