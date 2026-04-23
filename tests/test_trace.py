"""Tests for envoy.trace and envoy.cli_trace."""

from __future__ import annotations

import time

import pytest

from envoy.trace import (
    clear_traces,
    get_traces,
    record_trace,
    summary,
)
from envoy.cli_trace import (
    cmd_trace_clear,
    cmd_trace_record,
    cmd_trace_show,
    cmd_trace_summary,
)


@pytest.fixture()
def base_dir(tmp_path):
    return str(tmp_path)


# ---------------------------------------------------------------------------
# envoy.trace unit tests
# ---------------------------------------------------------------------------

def test_get_traces_empty_when_missing(base_dir):
    assert get_traces(base_dir=base_dir) == []


def test_record_trace_creates_entry(base_dir):
    record_trace("set", "prod", 12.5, base_dir=base_dir)
    traces = get_traces(base_dir=base_dir)
    assert len(traces) == 1
    assert traces[0]["operation"] == "set"
    assert traces[0]["profile"] == "prod"
    assert traces[0]["duration_ms"] == 12.5


def test_record_trace_stores_detail(base_dir):
    record_trace("get", "dev", 3.0, detail="KEY=FOO", base_dir=base_dir)
    traces = get_traces(base_dir=base_dir)
    assert traces[0]["detail"] == "KEY=FOO"


def test_record_multiple_traces(base_dir):
    for i in range(5):
        record_trace("list", "staging", float(i), base_dir=base_dir)
    assert len(get_traces(base_dir=base_dir)) == 5


def test_get_traces_filter_by_profile(base_dir):
    record_trace("set", "prod", 1.0, base_dir=base_dir)
    record_trace("set", "dev", 2.0, base_dir=base_dir)
    result = get_traces(profile="prod", base_dir=base_dir)
    assert len(result) == 1
    assert result[0]["profile"] == "prod"


def test_get_traces_filter_by_operation(base_dir):
    record_trace("set", "prod", 1.0, base_dir=base_dir)
    record_trace("get", "prod", 2.0, base_dir=base_dir)
    result = get_traces(operation="get", base_dir=base_dir)
    assert all(t["operation"] == "get" for t in result)


def test_get_traces_limit(base_dir):
    for i in range(10):
        record_trace("list", "prod", float(i), base_dir=base_dir)
    result = get_traces(limit=3, base_dir=base_dir)
    assert len(result) == 3


def test_clear_traces(base_dir):
    record_trace("set", "prod", 5.0, base_dir=base_dir)
    clear_traces(base_dir=base_dir)
    assert get_traces(base_dir=base_dir) == []


def test_summary_empty_when_no_traces(base_dir):
    assert summary(base_dir=base_dir) == {}


def test_summary_aggregates_correctly(base_dir):
    record_trace("set", "prod", 10.0, base_dir=base_dir)
    record_trace("set", "dev", 20.0, base_dir=base_dir)
    record_trace("get", "prod", 5.0, base_dir=base_dir)
    s = summary(base_dir=base_dir)
    assert s["set"]["count"] == 2
    assert s["set"]["avg_ms"] == 15.0
    assert s["set"]["max_ms"] == 20.0
    assert s["get"]["count"] == 1


# ---------------------------------------------------------------------------
# envoy.cli_trace integration tests
# ---------------------------------------------------------------------------

class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def make_args(**kw):
    defaults = {"base_dir": None, "profile": None, "operation": None, "limit": 50}
    defaults.update(kw)
    return _Args(**defaults)


def test_cmd_trace_show_empty(base_dir, capsys):
    cmd_trace_show(make_args(base_dir=base_dir))
    assert "No traces" in capsys.readouterr().out


def test_cmd_trace_show_displays_entries(base_dir, capsys):
    record_trace("set", "prod", 7.0, base_dir=base_dir)
    cmd_trace_show(make_args(base_dir=base_dir))
    out = capsys.readouterr().out
    assert "set" in out
    assert "prod" in out


def test_cmd_trace_summary_empty(base_dir, capsys):
    cmd_trace_summary(make_args(base_dir=base_dir))
    assert "No trace data" in capsys.readouterr().out


def test_cmd_trace_record_and_show(base_dir, capsys):
    args = make_args(
        base_dir=base_dir,
        operation="rotate",
        profile="qa",
        duration_ms=33.0,
        detail=None,
    )
    cmd_trace_record(args)
    assert "rotate" in capsys.readouterr().out
    traces = get_traces(base_dir=base_dir)
    assert len(traces) == 1
    assert traces[0]["operation"] == "rotate"


def test_cmd_trace_clear_removes_entries(base_dir, capsys):
    record_trace("set", "prod", 1.0, base_dir=base_dir)
    cmd_trace_clear(make_args(base_dir=base_dir))
    assert "cleared" in capsys.readouterr().out
    assert get_traces(base_dir=base_dir) == []
