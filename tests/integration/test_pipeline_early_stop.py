import pytest
from test_pipeline_engine import manifest

from agcws.reporting.metrics import summarize
from agcws.search.providers.recovery import RecoveryMeter as Meter
from agcws.studies import engine


def test_success_carries_terminal_error_without_fabricated_trials():
    rows = [
        {"slot": 1, "valid": False, "loss": None},
        {"slot": 2, "valid": True, "loss": 0.05},
    ]
    result = summarize(rows, 128, 0.1, stop_on_success=True)
    assert result["charged_slots"] == 2
    assert result["valid_slots"] == 1
    assert result["evaluations_to_target"] == 2
    assert result["curve"] == [1.0] + [0.05] * 127
    assert result["auc"] == pytest.approx(0.525 + 126 * 0.05)
    with pytest.raises(ValueError):
        summarize(rows, 128, 0.1)
    with pytest.raises(ValueError, match="tolerance hit"):
        summarize(rows, 128, 0.01, stop_on_success=True)


def test_batch_siblings_charged_and_resume_does_not_remeasure(tmp_path):
    from agcws.core.storage import write

    m = manifest(tmp_path, budget=8)
    m["spec"]["stop_on_success"] = True
    # manifest() writes the initial fixture; use a separate root for the changed spec.
    root = tmp_path / "early"
    root.mkdir()
    write(root / "manifest.json", m)
    measured = []

    def evaluator(proposal, slot, history, manifest, root, arm):
        measured.append(slot)
        assert history == []
        return {"valid": slot == 1, "loss": 0.0 if slot == 1 else None,
                "rates": [0.0] * 8 if slot == 1 else None}

    meter = Meter(root, 1)
    target = next(iter(m["spec"]["targets"]))
    first = engine.cell(root, m, target, 1, "random", meter, evaluator)
    second = engine.cell(root, m, target, 1, "random", meter, evaluator)
    assert first == second
    assert measured == [1, 2]
    assert first["charged_slots"] == 2
    assert first["evaluations_to_target"] == 1
    assert first["valid_slots"] == 1


def test_unsolved_budget_is_censored():
    rows = [{"slot": i, "valid": True, "loss": 0.2} for i in range(1, 9)]
    result = summarize(rows, 8, 0.1, stop_on_success=True)
    assert result["right_censored"]
    assert not result["stopped_early"]
    assert result["charged_slots"] == result["evaluations_to_target"] == 8
