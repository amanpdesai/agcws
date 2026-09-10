import copy
import random

import pytest

from experiments.baseline_panel_v1.audit import metrics
from experiments.baseline_panel_v1.policies import (
    ARMS,
    Control,
    NoScreen,
    witness_program,
)
from experiments.baseline_panel_v1.study import FAMILIES, choose
from experiments.ibex_temporal_v3.program import canonical
from experiments.saga_temporal_v1.policy import Policy


def feedback(request):
    return [
        {
            **p,
            "canonical_program": p["program"],
            "status": "MEASURED" if p["selected"] else "FILTERED",
            "valid": True if p["selected"] else None,
            "rates": [2.0] * 8 if p["selected"] else None,
            "loss": 0.2 if p["selected"] else None,
        }
        for p in request["proposals"]
    ]


def test_matched_first_post_bootstrap_pool_is_identical():
    screen = Policy(870, 16, [0.0] * 8, 10)
    control = NoScreen(870, 16, [0.0] * 8, 10)
    initial = [p.ask() for p in (screen, control)]
    assert initial[0] == initial[1]
    for policy, request in zip((screen, control), initial, strict=True):
        policy.tell(feedback(request))
    screened, full = screen.ask(), control.ask()
    for a, b in zip(screened["proposals"], full["proposals"], strict=True):
        assert {k: v for k, v in a.items() if k != "selected"} == {
            k: v for k, v in b.items() if k != "selected"
        }
    assert sum(p["selected"] for p in screened["proposals"]) == 2
    assert all(p["selected"] for p in full["proposals"])
    assert full["decision"]["predicted_rates"] is None


@pytest.mark.parametrize("arm", ARMS)
def test_controls_complete_charged_budget(arm):
    control = Control(arm, 870, 16, [0.0] * 8, 10)
    count = 0
    while control.used < control.budget:
        request = control.ask()
        for proposal in request["proposals"]:
            count += 1
            assert proposal["slot"] == count
            assert canonical(proposal["program"]) == proposal["program"]
            assert all(
                parent < request["proposals"][0]["slot"]
                for parent in proposal["parents"]
            )
        control.tell(feedback(request))
    assert count == 16
    with pytest.raises(RuntimeError):
        control.ask()


def test_initialization_contract():
    batches = {a: Control(a, 870, 16, [0.0] * 8, 10).ask()["proposals"] for a in ARMS}
    expected = [p["program"] for p in batches["random"]]
    for arm, batch in batches.items():
        assert [p["program"] for p in batch] == expected[
            : 2 if arm == "gest-batch2" else 4
        ]


@pytest.mark.parametrize("family", FAMILIES)
def test_constructor_is_deterministic_and_legal(family):
    left, right = random.Random(860), random.Random(860)
    for slot in range(1, 5):
        program = witness_program(family, left, slot)
        assert program == witness_program(family, right, slot)
        assert canonical(program) == program


def test_selection_keeps_failures_and_first_qualifying_slot():
    manifest = {
        "constructors": [{"name": f} for f in FAMILIES],
        "scale": 100,
        "minimum_range": 0.05,
    }
    rows = []
    for i, family in enumerate(FAMILIES):
        rows.extend(
            [
                {"constructor": family, "slot": 1, "valid": False, "rates": None},
                {
                    "constructor": family,
                    "slot": 2,
                    "valid": True,
                    "rates": [0.0, 10.0 + i] * 4,
                    "cache_id": str(i),
                },
                {
                    "constructor": family,
                    "slot": 3,
                    "valid": True,
                    "rates": [0.0, 20.0 + i] * 4,
                    "cache_id": str(i) + "x",
                },
            ]
        )
    before = copy.deepcopy(rows)
    assert all(t["witness_slot"] == 2 for t in choose(rows, manifest))
    assert rows == before
    rows[1]["valid"] = rows[2]["valid"] = False
    with pytest.raises(ValueError, match="no qualifying"):
        choose(rows, manifest)


def test_filtered_slots_carry_error_without_changing_unknown_validity():
    trials = [
        {"slot": i + 1, "status": s, "valid": v, "loss": loss}
        for i, (s, v, loss) in enumerate(
            [
                ("MEASURED", True, 0.4),
                ("FILTERED", None, None),
                ("MEASURED", True, 0.2),
                ("MEASURED", False, None),
            ]
        )
    ]
    report = metrics(trials, 4, 0.1)
    assert report["auc"] == pytest.approx(0.9)
    assert report["filtered"] == 1 and report["selected_evaluations"] == 3
    assert report["valid_slots"] == 2 and report["right_censored"]
    assert report["evaluations_to_target"] == 4
    assert trials[1]["valid"] is None
