import runpy

import pytest

from agcws.pipeline.storage import write


def test_comparison_ignores_runtime_cost_but_keeps_window_and_work():
    compare = runpy.run_path("analysis/runtime_replay.py")["comparable"]
    row = {"valid": True, "stage": None, "rates": [1]*8,
           "profile": {"clock_edges": 64, "useful_work": 16}, "evaluation_s": 1}
    assert compare(row) == compare({**row, "evaluation_s": 100})
    assert compare(row) != compare({**row, "profile": {"clock_edges": 65, "useful_work": 16}})


def test_replay_audit_rejects_changed_frozen_input(tmp_path):
    write(tmp_path / "freeze.json", {"expected.json": "incorrect"})
    write(tmp_path / "expected.json", {})
    with pytest.raises(ValueError, match="frozen replay inputs"):
        runpy.run_path("analysis/runtime_replay.py")["audit"](tmp_path)
