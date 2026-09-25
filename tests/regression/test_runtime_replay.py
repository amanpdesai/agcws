import pytest

from agcws.core.storage import write
from agcws.evidence.replay import comparable_measurement as compare
from agcws.evidence.replay import verify_frozen_inputs


def test_comparison_ignores_runtime_cost_but_keeps_window_and_work():
    row = {"valid": True, "stage": None, "rates": [1]*8,
           "profile": {"clock_edges": 64, "useful_work": 16}, "evaluation_s": 1}
    assert compare(row) == compare({**row, "evaluation_s": 100})
    assert compare(row) != compare({**row, "profile": {"clock_edges": 65, "useful_work": 16}})


def test_replay_audit_rejects_changed_frozen_input(tmp_path):
    write(tmp_path / "freeze.json", {"expected.json": "incorrect"})
    write(tmp_path / "expected.json", {})
    with pytest.raises(ValueError, match="frozen replay inputs"):
        verify_frozen_inputs(tmp_path)
