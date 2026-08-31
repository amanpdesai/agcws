from pathlib import Path

from agcws.tasks import TaskStore


def test_task_store_invalidates_changed_inputs(tmp_path: Path):
    store = TaskStore(tmp_path / "tasks")
    calls = []

    def action(output: Path):
        calls.append(output)
        (output / "result.json").write_text('{"ok": true}\n')

    first = store.run("evaluate", {"workload": "one"}, action)
    second = store.run("evaluate", {"workload": "two"}, action)
    assert first.key != second.key
    assert not first.cached and not second.cached
    assert len(calls) == 2
