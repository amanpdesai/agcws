import json
import random

import pytest

from experiments.ibex_temporal_v3.feedback import CLASSES
from experiments.ibex_temporal_v3.program import allocation, random_program
from experiments.ibex_temporal_v4 import search


@pytest.mark.parametrize("short", [False, True])
def test_predictions_precede_evaluation_and_no_same_batch_reference(
    tmp_path, monkeypatch, short
):
    manifest = {
        "targets": {"t": {"rates": [1] * 8}},
        "seeds": [600],
        "policies": ["agent-grounded"],
        "model": "fake",
        "scale": 100,
        "tolerance": 0.1,
        "budget": 4,
        "measurement_fingerprint": "fake",
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    monkeypatch.setattr(search, "verify_runtime", lambda *_: None)
    monkeypatch.setattr(search.subprocess, "check_output", lambda *_: path.read_bytes())
    monkeypatch.setattr(search.config, "_load_dotenv", lambda: None)
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "fake")
    monkeypatch.setattr(search, "client", lambda *_: None)
    p = random_program(random.Random(4))
    generated = {
        "hypothesis": "test",
        "candidates": [p] if short else [p, p],
        "predictions": [
            {
                "reference_slot": 1,
                "changed_factor": "test",
                "window_directions": [0] * 8,
            },
            {
                "reference_slot": 3,
                "changed_factor": "test",
                "window_directions": [0] * 8,
            },
        ],
    }
    calls = []

    def request(*args):
        calls.append(args)
        return {
            "raw_text": json.dumps(generated),
            "tokens_in": 3,
            "tokens_out": 5,
            "est_cost_usd": 0.1,
            "usage_unknown": False,
        }

    monkeypatch.setattr(search, "request", request)
    output = tmp_path / "panel/t/seed-600/agent-grounded"
    measured = []

    def evaluate(program, *_):
        batches = json.loads((output / "batches.json").read_text())
        if len(measured) >= 2:
            assert batches[-1]["decoded"]["hypothesis"] == "test"
        measured.append(program)
        if program is None:
            return {"valid": False, "stage": "SCHEMA", "reason": "missing"}, False
        return {
            "valid": True,
            "stage": None,
            "reason": "",
            "cache_id": "fake",
            "allocation": allocation(program),
            "profile": {"window_rates": [1] * 8},
            "feedback": {
                "cycles_per_bin": 25000,
                "cycles_without_retirement": [24999] * 8,
                "retired_classes": [
                    {k: int(k == "alu") for k in CLASSES} for _ in range(8)
                ],
            },
            "execution": {},
        }, False

    monkeypatch.setattr(search, "measured", evaluate)
    search.search(path, tmp_path, "t", "agent-grounded", 600)
    rows = [json.loads(l) for l in (output / "trials.jsonl").read_text().splitlines()]
    assert len(calls) == 1 and len(rows) == 4
    assert sum(t["tokens_in"] for t in rows) == 3
    assert sum(t["tokens_out"] for t in rows) == 5
    assert rows[2]["prediction_assessment"]["scorable"]
    assert not rows[3]["prediction_assessment"]["scorable"]
    if short:
        assert rows[3]["stage"] == "SCHEMA"
    else:
        assert rows[3]["valid"]
        assert (
            rows[3]["prediction_error"]
            == "reference was not visible as valid before this batch"
        )


def test_cache_schema_failure_cannot_start_tools(tmp_path):
    from experiments.ibex_temporal_v4.cache import measured

    result, hit = measured(
        {"program": random_program(random.Random(4))}, tmp_path, "test"
    )
    assert not result["valid"] and result["stage"] == "SCHEMA"
    assert not hit and not (tmp_path / "cache").exists()
