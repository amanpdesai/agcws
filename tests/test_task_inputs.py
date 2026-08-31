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


def test_task_store_does_not_cache_failed_action(tmp_path: Path):
    store = TaskStore(tmp_path / "tasks")
    calls = []

    def failing(output: Path):
        calls.append(output)
        raise RuntimeError("simulated interruption")

    try:
        store.run("evaluate", {"workload": "one"}, failing)
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected action failure")

    manifest = calls[0] / "task.json"
    assert '"status": "running"' in manifest.read_text()
    recovered = store.run("evaluate", {"workload": "one"},
                          lambda output: (output / "result.json").write_text("{}\n"))
    assert recovered.cached is False
    assert '"status": "complete"' in manifest.read_text()
