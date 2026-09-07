import json
import random
import threading

import pytest

from experiments.ibex_capability_v1 import study
from experiments.ibex_temporal_v3.program import random_program
from experiments.ibex_temporal_v4.contract import decode


def test_settings_factorial_changes_only_model_tier_and_thinking_budget():
    arms = [study.settings(a) for a in study.MODEL_ARMS]
    assert {(a["model"], a["thinking_budget"]) for a in arms} == {
        (f"gemini-2.5-{tier}", budget)
        for tier in ("flash", "pro")
        for budget in (512, 4096)
    }
    assert all(a["max_output_tokens"] == 16384 for a in arms)
    assert (
        study.estimate({"tokens_in": 200001, "tokens_out": 100}, "pro-4096")
        == (200001 * 2.5 + 100 * 15) / 1e6
    )


def test_primary_keeps_failed_slots_and_distinguishes_new_solves():
    history = [{"valid": True, "loss": 0.4}]
    trials = [{"valid": False, "loss": None}, {"valid": True, "loss": 0.08}]
    result = study.summarize_slots(history, trials, 0.1)
    assert result["gain"] == pytest.approx(0.32)
    assert result["requested_slots"] == 2 and result["valid_slots"] == 1
    assert result["newly_solved"] and not result["already_solved"]
    result = study.summarize_slots([{"valid": True, "loss": 0.05}], trials, 0.1)
    assert result["gain"] == 0 and not result["newly_solved"]


def test_durable_response_reused_and_interrupted_request_not_reissued(
    tmp_path, monkeypatch
):
    archive, output = tmp_path / "archive", tmp_path / "output"
    study.write(archive / "manifest.json", {})
    study.write(archive / "contexts/c.json", [])
    study.write(archive / "payloads/c.json", {})
    study.write(archive / "schema.json", {})
    cell = {"context": "c", "arm": "pro-4096", "seed": 1}
    manifest = {"arms": {"pro-4096": study.settings("pro-4096")}}
    calls = []
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "test-project")
    monkeypatch.setattr(study, "client", lambda _: None)

    def request(api, model, contents, settings, schema):
        calls.append(settings)
        assert (output / "cells/c/pro-4096/request_started.json").exists()
        return {
            "raw_text": "{}",
            "tokens_in": 100,
            "tokens_out": 20,
            "usage_unknown": False,
            "est_cost_usd": 0.0,
        }

    monkeypatch.setattr(study, "request", request)
    first = study.generate(cell, archive, output, manifest, threading.Lock())
    second = study.generate(cell, archive, output, manifest, threading.Lock())
    assert first == second and len(calls) == 1
    assert calls[0]["thinking_budget"] == 4096
    assert len(first["decoded"]["slots"]) == 2
    (output / "cells/c/pro-4096/response.json").unlink()
    with pytest.raises(FileExistsError):
        study.generate(cell, archive, output, manifest, threading.Lock())
    assert len(calls) == 1


def test_same_batch_predictions_are_not_visible_and_response_precedes_sim(
    tmp_path, monkeypatch
):
    archive, output = tmp_path / "archive", tmp_path / "output"
    program = random_program(random.Random(5))
    history = [
        {
            "slot": 1,
            "valid": True,
            "loss": 0.5,
            "rates": [1] * 8,
            "program": program,
            "canonical_program": program,
        }
    ]
    study.write(archive / "contexts/c.json", history)
    cell = {"context": "c", "arm": "pro-4096", "seed": 1}
    response = {
        "decoded": decode(
            json.dumps(
                {
                    "hypothesis": "test",
                    "candidates": [program, program],
                    "predictions": [
                        {
                            "reference_slot": s,
                            "changed_factor": "test",
                            "window_directions": [0] * 8,
                        }
                        for s in (1, 7)
                    ],
                }
            ),
            2,
            True,
        )
    }
    response_path = output / "cells/c/pro-4096/response.json"

    def generate(*args):
        study.write(response_path, response)
        return response

    def measured(*args):
        assert response_path.exists()
        return {
            "valid": True,
            "cache_id": "mock",
            "stage": None,
            "profile": {"window_rates": [1] * 8},
        }, False

    monkeypatch.setattr(study, "generate", generate)
    monkeypatch.setattr(study, "measured", measured)
    result = study.evaluate_cell(
        cell,
        archive,
        output,
        {
            "contexts": {"c": {"target": "t"}},
            "measurement_fingerprint": "mock",
        },
        {"targets": {"t": {"rates": [0] * 8}}, "scale": 10, "tolerance": 0.1},
        threading.Lock(),
    )
    assert result["trials"][0]["prediction_assessment"]["scorable"]
    assert not result["trials"][1]["prediction_assessment"]["scorable"]
    assert all(t["valid"] for t in result["trials"])


def test_endpoint_failure_stops_before_remaining_cells(tmp_path, monkeypatch):
    cells = [{"context": "c", "arm": a} for a in study.ARMS]
    monkeypatch.setattr(
        study, "verify_inputs", lambda *_: ({"cells": cells, "max_workers": 4}, {})
    )
    monkeypatch.setattr(study.config, "_load_dotenv", lambda: None)
    calls = []

    def generate(cell, *args):
        calls.append(cell)
        return {"cell": cell, "usage_unknown": cell["arm"] == "pro-512"}

    monkeypatch.setattr(study, "generate", generate)
    with pytest.raises(RuntimeError, match="acceptance failed"):
        study.run(tmp_path, tmp_path, 4)
    assert calls == cells[:4]
    assert not study.read(tmp_path / "endpoint_gate.json")["ready"]
