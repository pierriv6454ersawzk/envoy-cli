import pytest
from pathlib import Path
from envoy.note import set_note, get_note, remove_note, list_notes


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def test_set_and_get_profile_note(base_dir):
    set_note("prod", "Production environment", base_dir=base_dir)
    assert get_note("prod", base_dir=base_dir) == "Production environment"


def test_set_and_get_key_note(base_dir):
    set_note("prod", "Database password", key="DB_PASS", base_dir=base_dir)
    assert get_note("prod", key="DB_PASS", base_dir=base_dir) == "Database password"


def test_get_note_returns_none_when_missing(base_dir):
    assert get_note("missing", base_dir=base_dir) is None
    assert get_note("missing", key="FOO", base_dir=base_dir) is None


def test_set_note_overwrites_existing(base_dir):
    set_note("dev", "first", base_dir=base_dir)
    set_note("dev", "second", base_dir=base_dir)
    assert get_note("dev", base_dir=base_dir) == "second"


def test_remove_note_returns_true_when_exists(base_dir):
    set_note("dev", "some note", base_dir=base_dir)
    assert remove_note("dev", base_dir=base_dir) is True
    assert get_note("dev", base_dir=base_dir) is None


def test_remove_note_returns_false_when_missing(base_dir):
    assert remove_note("ghost", base_dir=base_dir) is False


def test_list_notes_returns_all(base_dir):
    set_note("staging", "Staging env", base_dir=base_dir)
    set_note("staging", "API token", key="API_TOKEN", base_dir=base_dir)
    notes = list_notes("staging", base_dir=base_dir)
    assert notes["__profile__"] == "Staging env"
    assert notes["__key__API_TOKEN"] == "API token"


def test_list_notes_empty_when_none(base_dir):
    assert list_notes("nobody", base_dir=base_dir) == {}


def test_remove_key_note_leaves_profile_note(base_dir):
    set_note("prod", "prod note", base_dir=base_dir)
    set_note("prod", "key note", key="SECRET", base_dir=base_dir)
    remove_note("prod", key="SECRET", base_dir=base_dir)
    assert get_note("prod", base_dir=base_dir) == "prod note"
    assert get_note("prod", key="SECRET", base_dir=base_dir) is None
