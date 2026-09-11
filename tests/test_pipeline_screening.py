import copy
import math
import random

import numpy as np
import pytest

from agcws.pipeline.ibex.program import random_program
from agcws.pipeline.policies.screening import Policy
from agcws.pipeline.policies.surrogate import (
    Ridge,
    features,
    screen,
    training_rows,
)


def history():
    return [
        {
            "slot": i + 1,
            "program": random_program(random.Random(i)),
            "valid": True,
            "status": "MEASURED",
            "rates": [10.0 + i] * 8,
        }
        for i in range(4)
    ]


def feedback(batch):
    rows = []
    for p in batch["proposals"]:
        row = {
            **p,
            "status": "MEASURED" if p["selected"] else "FILTERED",
            "valid": True if p["selected"] else None,
            "loss": 0.2 if p["selected"] else None,
            "rates": [2.0] * 8 if p["selected"] else None,
        }
        rows.append(row)
    return rows


def test_features_observe_phase_order_and_timing():
    p = random_program(random.Random(2))
    p["segments"] = [copy.deepcopy(p["segments"][0]), copy.deepcopy(p["segments"][0])]
    p["segments"][0]["release"] = 0
    p["segments"][1]["release"] = 100000
    swapped = copy.deepcopy(p)
    swapped["segments"].reverse()
    assert not np.array_equal(features(p), features(swapped))
    assert features(p).shape == features(random_program(random.Random(1))).shape
    assert np.isfinite(features(p)).all()


def test_fit_and_selection_are_deterministic():
    rows = history()
    programs = [t["program"] for t in rows]
    a = screen(programs, rows, [12.0] * 8, 10)
    assert a == screen(programs, rows, [12.0] * 8, 10)
    assert len(set(a["selected_indices"])) == 2
    assert a["training_slots"] == [1, 2, 3, 4]


def test_training_excludes_unmeasured_invalid_and_duplicates():
    rows = history()
    rows[1] = {**rows[0], "slot": 2}
    rows[2]["status"] = "FILTERED"
    assert [r["slot"] for r in training_rows(rows)] == [1, 4]
    rows[3]["valid"] = False
    with pytest.raises(ValueError, match="two distinct"):
        Ridge(rows, 10)


def test_bad_measurements_fail_closed():
    rows = history()
    rows[0]["rates"][0] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        Ridge(rows, 10)
    with pytest.raises(ValueError, match="positive"):
        Ridge(history(), 10, alpha=0)


def test_complete_accounting_and_history_isolation():
    policy = Policy(850, 12, [0.0] * 8, 10)
    measured = filtered = 0
    for offset in (0, 4, 8):
        before = copy.deepcopy(policy._history)
        batch = policy.ask()
        assert policy._history == before
        assert all(s <= offset for s in batch["decision"]["training_slots"])
        records = feedback(batch)
        measured += sum(r["selected"] for r in records)
        filtered += sum(not r["selected"] for r in records)
        policy.tell(records)
    assert (policy.used, measured, filtered) == (12, 8, 4)
    assert len(policy._parents) == 8
    with pytest.raises(RuntimeError, match="exhausted"):
        policy.ask()


def test_predicted_score_cannot_become_measurement():
    policy = Policy(1, 8, [0.0] * 8, 10)
    policy.tell(feedback(policy.ask()))
    batch = policy.ask()
    records = feedback(batch)
    next(r for r in records if not r["selected"])["loss"] = 0.1
    with pytest.raises(ValueError, match="unknown validity"):
        policy.tell(records)
    assert len(policy._history) == 4
    records = feedback(batch)
    next(r for r in records if r["selected"])["loss"] = 0.123
    with pytest.raises(ValueError, match="match measured"):
        policy.tell(records)


def test_failed_bootstrap_does_not_resample():
    policy = Policy(1, 8, [0.0] * 8, 10)
    records = feedback(policy.ask())
    for r in records:
        r.update(valid=False, rates=None, loss=None, stage="USEFUL_WORK", reason="floor")
    policy.tell(records)
    with pytest.raises(ValueError, match="no replacement"):
        policy.ask()
    assert policy.used == 4


def test_prediction_error_is_not_training_fit_quality():
    model = Ridge(history(), 10)
    prediction = model.predict(random_program(random.Random(9)))
    assert len(prediction) == 8 and all(math.isfinite(v) for v in prediction)


def test_fit_failure_charges_generated_pool_and_cannot_retry(monkeypatch):
    policy = Policy(1, 8, [0.0] * 8, 10)
    policy.tell(feedback(policy.ask()))

    def fail(*args):
        raise np.linalg.LinAlgError("intentional fit failure")

    monkeypatch.setattr("agcws.pipeline.policies.screening.screen", fail)
    with pytest.raises(np.linalg.LinAlgError, match="intentional"):
        policy.ask()
    assert policy.used == 8 and len(policy._pending) == 4
    assert len(policy._history) == 4
    with pytest.raises(RuntimeError, match="pending"):
        policy.ask()


def test_duplicate_feedback_and_missing_slots_are_rejected():
    policy = Policy(1, 8, [0.0] * 8, 10)
    batch = policy.ask()
    with pytest.raises(ValueError, match="four-slot"):
        policy.tell(feedback(batch)[:3])
    policy.tell(feedback(batch))
    with pytest.raises(ValueError, match="four-slot"):
        policy.tell(feedback(batch))


def test_filtering_cannot_import_current_batch_labels():
    policy = Policy(1, 8, [0.0] * 8, 10)
    policy.tell(feedback(policy.ask()))
    batch = policy.ask()
    expected = copy.deepcopy(batch)
    batch["proposals"][0]["program"]["registers"][0] ^= 1
    assert all(i <= 4 for i in expected["decision"]["training_slots"])
    policy.tell(feedback(expected))
    assert len(policy._parents) == 6


@pytest.mark.parametrize("budget", [0, 4, 6, True, 8.0])
def test_budget_shape_is_explicit(budget):
    with pytest.raises(ValueError, match="multiple"):
        Policy(1, budget, [0.0] * 8, 10)
