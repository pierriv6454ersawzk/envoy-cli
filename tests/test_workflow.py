import pytest
from envoy.workflow import (
    save_workflow,
    load_workflow,
    delete_workflow,
    list_workflows,
    WorkflowError,
)


@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)


def _simple_steps():
    return [
        {"action": "set", "key": "FOO", "value": "bar"},
        {"action": "export", "path": "/tmp/out.env"},
    ]


def test_save_and_list_workflow(base_dir):
    save_workflow("deploy", _simple_steps(), base_dir=base_dir)
    assert "deploy" in list_workflows(base_dir=base_dir)


def test_load_workflow_returns_steps(base_dir):
    save_workflow("deploy", _simple_steps(), base_dir=base_dir)
    steps = load_workflow("deploy", base_dir=base_dir)
    assert steps[0]["action"] == "set"
    assert steps[1]["action"] == "export"


def test_load_missing_workflow_raises(base_dir):
    with pytest.raises(WorkflowError, match="not found"):
        load_workflow("ghost", base_dir=base_dir)


def test_save_workflow_invalid_name_raises(base_dir):
    with pytest.raises(WorkflowError, match="Invalid workflow name"):
        save_workflow("bad-name!", _simple_steps(), base_dir=base_dir)


def test_save_workflow_invalid_step_raises(base_dir):
    bad_steps = [{"action": "teleport", "destination": "moon"}]
    with pytest.raises(WorkflowError, match="Unknown step action"):
        save_workflow("bad", bad_steps, base_dir=base_dir)


def test_save_workflow_overwrites_existing(base_dir):
    save_workflow("deploy", _simple_steps(), base_dir=base_dir)
    new_steps = [{"action": "delete", "key": "OLD"}]
    save_workflow("deploy", new_steps, base_dir=base_dir)
    steps = load_workflow("deploy", base_dir=base_dir)
    assert len(steps) == 1
    assert steps[0]["action"] == "delete"


def test_delete_workflow(base_dir):
    save_workflow("deploy", _simple_steps(), base_dir=base_dir)
    delete_workflow("deploy", base_dir=base_dir)
    assert "deploy" not in list_workflows(base_dir=base_dir)


def test_delete_missing_workflow_raises(base_dir):
    with pytest.raises(WorkflowError, match="not found"):
        delete_workflow("ghost", base_dir=base_dir)


def test_list_workflows_empty_when_none(base_dir):
    assert list_workflows(base_dir=base_dir) == []


def test_list_workflows_sorted(base_dir):
    save_workflow("zebra", _simple_steps(), base_dir=base_dir)
    save_workflow("alpha", _simple_steps(), base_dir=base_dir)
    names = list_workflows(base_dir=base_dir)
    assert names == ["alpha", "zebra"]
