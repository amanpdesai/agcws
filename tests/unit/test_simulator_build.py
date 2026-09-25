import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from agcws.core.build import ensure_binary


def executable(path):
    path.write_text("simulator fixture")
    path.chmod(0o755)


def test_parallel_compile_publishes_once(tmp_path):
    start = threading.Barrier(8)
    calls = []

    def compile_binary(path):
        calls.append(path)
        executable(path)

    def worker(_):
        start.wait()
        return ensure_binary(tmp_path, "simulate", compile_binary)

    with ThreadPoolExecutor(max_workers=8) as pool:
        paths = list(pool.map(worker, range(8)))
    assert paths == [tmp_path / "simulate"] * 8
    assert len(calls) == 1


def test_failed_compile_does_not_publish_and_can_resume(tmp_path):
    def failed(path):
        executable(path)
        raise RuntimeError("compiler failed after writing output")

    with pytest.raises(RuntimeError):
        ensure_binary(tmp_path, "simulate", failed)
    assert not (tmp_path / "simulate.complete.json").exists()
    calls = []

    def finish(path):
        calls.append(path)
        executable(path)

    ensure_binary(tmp_path, "simulate", finish)
    assert len(calls) == 1


def test_changed_completed_binary_is_rejected(tmp_path):
    ensure_binary(tmp_path, "simulate", executable)
    (tmp_path / "simulate").write_text("changed")
    with pytest.raises(ValueError, match="modified"):
        ensure_binary(tmp_path, "simulate", executable)


def test_missing_executable_is_not_success(tmp_path):
    with pytest.raises(ValueError, match="executable"):
        ensure_binary(tmp_path, "simulate", lambda path: path.write_text("not executable"))
    assert not (tmp_path / "simulate.complete.json").exists()
