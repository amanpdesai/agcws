from pathlib import Path

from agcws.tasks import TaskStore, file_digest, task_key


def test_task_key_is_order_independent():
    assert task_key("simulate", {"b": 2, "a": 1}) == task_key("simulate", {"a": 1, "b": 2})


def test_task_store_resumes_completed_task(tmp_path: Path):
    calls = []
    store = TaskStore(tmp_path / "tasks")

    def action(output: Path):
        calls.append(output)
        (output / "result.json").write_text("{}\n")

    first = store.run("simulate", {"workload_sha256": "abc"}, action)
    second = store.run("simulate", {"workload_sha256": "abc"}, action)

    assert first.cached is False
    assert second.cached is True
    assert len(calls) == 1
    assert file_digest(first.manifest) == file_digest(second.manifest)


def test_task_key_changes_when_toolchain_changes():
    base = {"workload_sha256": "abc", "tools": {"opensta": "3.1.0"}}
    changed = {"workload_sha256": "abc", "tools": {"opensta": "3.2.0"}}
    assert task_key("evaluate", base) != task_key("evaluate", changed)
