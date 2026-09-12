import copy
import json
from pathlib import Path

import pytest

from validation.phase_ga_gate import compare


def fixture():
    sample = json.loads(Path("results/evidence_extension_v1/workloads/ibex_low.json").read_text())
    record = {
        "valid": True,
        "stage": None,
        "reason": "",
        "allocation": sample["allocation"],
        "profile": sample["profile"],
    }
    run = {
        "assembly": b"instructions",
        "functional": {
            "expected": {"registers": [0] * 8},
            "functional_ok": True,
            "marker_pcs": {"begin": 4},
        },
    }
    return record, run, [{"id": "target", "rates": sample["profile"]["window_rates"]}]


def test_exact_gate_accepts_identity_and_ignores_timing_cost():
    old, run, targets = fixture()
    new = copy.deepcopy(old)
    new["profile"]["extraction_s"] = 999
    assert compare(old, new, run, run, targets, 528.45376)["passed"]


@pytest.mark.parametrize(
    "field", ["window_bit_transitions", "window_rates", "end_tick", "unknown_events"]
)
def test_gate_rejects_even_one_count_or_window_change(field):
    old, run, targets = fixture()
    new = copy.deepcopy(old)
    if isinstance(new["profile"][field], list):
        new["profile"][field][0] += 1
    else:
        new["profile"][field] += 1
    report = compare(old, new, run, run, targets, 528.45376)
    assert not report["passed"] and not report["checks"]["profile." + field]


@pytest.mark.parametrize("field", ["assembly", "reference_state", "marker_pcs"])
def test_gate_rejects_compiler_or_reference_drift(field):
    record, run, targets = fixture()
    changed = copy.deepcopy(run)
    if field == "assembly":
        changed["assembly"] += b"changed"
    elif field == "reference_state":
        changed["functional"]["expected"]["registers"][0] = 1
    else:
        changed["functional"]["marker_pcs"]["begin"] = 8
    assert not compare(record, record, run, changed, targets, 528.45376)["passed"]
