import pytest
from envoy.priority import set_priority, remove_priority, get_priority, list_priorities, PriorityError
from envoy.vault import save


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _seed(base_dir, profile="default"):
    save({"KEY": "val"}, profile, "pass", base_dir)


def test_get_priority_returns_zero_when_missing(base_dir):
    _seed(base_dir)
    assert get_priority(base_dir, "default") == 0


def test_set_and_get_priority(base_dir):
    _seed(base_dir)
    set_priority(base_dir, "default", 10)
    assert get_priority(base_dir, "default") == 10


def test_set_priority_overwrites_existing(base_dir):
    _seed(base_dir)
    set_priority(base_dir, "default", 5)
    set_priority(base_dir, "default", 99)
    assert get_priority(base_dir, "default") == 99


def test_set_priority_missing_profile_raises(base_dir):
    with pytest.raises(PriorityError, match="does not exist"):
        set_priority(base_dir, "ghost", 1)


def test_set_priority_negative_raises(base_dir):
    _seed(base_dir)
    with pytest.raises(PriorityError, match="non-negative"):
        set_priority(base_dir, "default", -1)


def test_remove_priority(base_dir):
    _seed(base_dir)
    set_priority(base_dir, "default", 7)
    remove_priority(base_dir, "default")
    assert get_priority(base_dir, "default") == 0


def test_list_priorities_sorted_descending(base_dir):
    for name, val in [("a", 1), ("b", 5), ("c", 3)]:
        _seed(base_dir, name)
        set_priority(base_dir, name, val)
    result = list_priorities(base_dir)
    priorities = [p for _, p in result]
    assert priorities == sorted(priorities, reverse=True)


def test_list_priorities_empty(base_dir):
    assert list_priorities(base_dir) == []
