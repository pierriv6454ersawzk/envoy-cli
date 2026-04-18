"""Tests for envoy.remind."""
import time
import pytest
from envoy.remind import set_reminder, remove_reminder, get_reminder, list_reminders, due_reminders, ReminderError
from envoy.vault import save


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile="default"):
    save({"KEY": "val"}, profile, "pass", base_dir)


def test_set_and_get_reminder(base_dir):
    _seed(base_dir)
    due = time.time() + 3600
    set_reminder(base_dir, "default", "KEY", "Check this!", due)
    r = get_reminder(base_dir, "default", "KEY")
    assert r is not None
    assert r["message"] == "Check this!"
    assert abs(r["due"] - due) < 0.01


def test_get_reminder_returns_none_when_missing(base_dir):
    _seed(base_dir)
    assert get_reminder(base_dir, "default", "MISSING") is None


def test_set_reminder_missing_profile_raises(base_dir):
    with pytest.raises(ReminderError, match="does not exist"):
        set_reminder(base_dir, "ghost", "KEY", "msg", time.time() + 100)


def test_set_reminder_past_due_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(ReminderError, match="future"):
        set_reminder(base_dir, "default", "KEY", "msg", time.time() - 1)


def test_remove_reminder_returns_true(base_dir):
    _seed(base_dir)
    set_reminder(base_dir, "default", "KEY", "msg", time.time() + 100)
    assert remove_reminder(base_dir, "default", "KEY") is True
    assert get_reminder(base_dir, "default", "KEY") is None


def test_remove_missing_reminder_returns_false(base_dir):
    _seed(base_dir)
    assert remove_reminder(base_dir, "default", "NOPE") is False


def test_list_reminders_empty(base_dir):
    _seed(base_dir)
    assert list_reminders(base_dir, "default") == {}


def test_list_reminders_multiple(base_dir):
    _seed(base_dir)
    set_reminder(base_dir, "default", "A", "msg A", time.time() + 100)
    set_reminder(base_dir, "default", "B", "msg B", time.time() + 200)
    result = list_reminders(base_dir, "default")
    assert set(result.keys()) == {"A", "B"}


def test_due_reminders_returns_only_overdue(base_dir, monkeypatch):
    _seed(base_dir)
    future = time.time() + 9999
    past = time.time() + 1
    set_reminder(base_dir, "default", "FUTURE", "not yet", future)
    set_reminder(base_dir, "default", "PAST", "overdue", past)
    monkeypatch.setattr("envoy.remind.time.time", lambda: past + 10)
    overdue = due_reminders(base_dir, "default")
    assert "PAST" in overdue
    assert "FUTURE" not in overdue
