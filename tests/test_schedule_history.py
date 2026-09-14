import copy
import hashlib
import json

from agcws.pipeline.backends import backend
from agcws.pipeline.schedules import history_summary


def trial(slot, valid=True):
    return {"slot": slot, "program": {"sequence": [{"op": "work", "units": 64},
                                                   {"op": "wait", "cycles": 6000}]},
            "valid": valid, "loss": slot / 100 if valid else None,
            "reason": "" if valid else "budget mismatch", "stage": None if valid else "PROTOCOL",
            "rates": [1.0]*8 if valid else None, "residual": [0.1]*8 if valid else None}


def test_fixed_selection_keeps_best_and_recent_with_no_future_or_mutation():
    history = [trial(i, i % 2 == 0) for i in range(1, 127)]
    original = copy.deepcopy(history)
    rows = history_summary(history)
    assert [r["slot"] for r in rows] == [2, 4, 6, 8, 123, 124, 125, 126]
    assert history == original
    assert history_summary(history[:8]) == history[:8]


def test_oversized_malformed_data_is_explicitly_omitted_not_repaired():
    row = trial(1, False)
    row.update(program={"invalid": "x"*100000}, reason="bad"*20000)
    result = history_summary([row])[0]
    assert result["valid"] is False and result["loss"] is None
    assert result["program"] is None
    assert result["program_omitted"]["sha256"] == hashlib.sha256(json.dumps(row["program"], sort_keys=True).encode()).hexdigest()
    assert result["reason"] is None and result["reason_excerpt"]["complete"] is False
    assert row["program"] is not None


def test_128_slot_adversarial_history_stays_under_request_guard():
    history = [trial(i, False) for i in range(1, 127)]
    for row in history:
        row.update(program={"malformed": "x"*100000}, reason="y"*100000)
    for domain in ("aes-temporal", "dma-temporal", "mesh-temporal", "redmule-temporal-long"):
        design = backend(domain)
        text = design.payload(history, {"profile": [1]*8, "scale": 10, "tolerance": .1}, 2)
        value = json.loads(text)
        assert value["history_policy"]["total_slots"] == 126
        assert [r["slot"] for r in value["history"]] == [123, 124, 125, 126]
        assert len(text.encode()) + len(json.dumps(design.schema(2)).encode()) + 4096 < 200000


def test_resource_guidance_uses_contract_not_design_specific_examples():
    for domain in ("aes-temporal", "dma-temporal", "mesh-temporal", "redmule-temporal-long"):
        design = backend(domain)
        value = json.loads(design.payload([], {"profile": [1]*8, "scale": 10, "tolerance": .1}, 2))
        if domain in ("aes-temporal", "dma-temporal"):
            assert value["exact_resource_budget"]["work_units"] == 64
            assert value["exact_resource_budget"]["idle_cycles"] == 6000
            assert "not automatic repairs" in value["exact_resource_budget"]["refinement_guidance"]
        else:
            assert "exact_resource_budget" not in value
