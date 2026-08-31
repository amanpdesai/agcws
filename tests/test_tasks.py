from pathlib import Path
import json
import multiprocessing
import pytest
import time

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


def test_task_reexecutes_when_required_output_is_missing(tmp_path: Path):
    calls = []
    store = TaskStore(tmp_path / "tasks")

    def action(output: Path):
        calls.append(output)
        (output / "result.json").write_text("{}\n")

    first = store.run("evaluate", {"input": "a"}, action,
                      required_outputs=("result.json",))
    (first.output_dir / "result.json").unlink()
    second = store.run("evaluate", {"input": "a"}, action,
                       required_outputs=("result.json",))

    assert second.cached is False
    assert len(calls) == 2


def test_task_rejects_incomplete_action(tmp_path: Path):
    store = TaskStore(tmp_path / "tasks")
    with pytest.raises(FileNotFoundError, match="required outputs"):
        store.run("evaluate", {}, lambda output: None,
                  required_outputs=("result.json",))


def test_task_records_failure_reason(tmp_path: Path):
    store = TaskStore(tmp_path / "tasks")

    def action(output: Path):
        raise RuntimeError("simulator exploded")

    with pytest.raises(RuntimeError, match="simulator exploded"):
        store.run("simulate", {}, action)
    manifest = next((tmp_path / "tasks" / "simulate").glob("*/task.json"))
    record = json.loads(manifest.read_text())
    assert record["status"] == "failed"
    assert "simulator exploded" in record["error"]


def test_task_rejects_output_path_escape(tmp_path: Path):
    store = TaskStore(tmp_path / "tasks")
    with pytest.raises(ValueError, match="inside task directory"):
        store.run("evaluate", {}, lambda output: None,
                  required_outputs=("../result.json",))


def test_task_store_serializes_same_key_across_processes(tmp_path: Path):
    calls = tmp_path / "calls"

    def worker(root: str, marker: str) -> None:
        def action(output: Path):
            calls_path = Path(root) / "calls"
            calls_path.write_text(
                calls_path.read_text() + marker if calls_path.exists() else marker
            )
            time.sleep(0.05)
            (output / "result.txt").write_text("ok")

        TaskStore(Path(root) / "tasks").run(
            "evaluate", {"input": "same"}, action,
            required_outputs=("result.txt",),
        )

    processes = [multiprocessing.Process(target=worker, args=(str(tmp_path), str(index)))
                 for index in range(2)]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
        assert process.exitcode == 0
    assert calls.read_text() in {"0", "1"}
