import json
import random
from types import SimpleNamespace as NS

import pytest

from experiments.ibex_depth_v1 import model, study
from experiments.ibex_depth_v1.metrics import summarize
from experiments.ibex_depth_v1.storage import ensure, read, write
from experiments.ibex_temporal_v3.feedback import CLASSES
from experiments.ibex_temporal_v3.program import allocation, random_program


def test_immutable_checkpoint(tmp_path):
    path = tmp_path / "record.json"
    write(path, {"a": 1})
    ensure(path, {"a": 1})
    with pytest.raises(FileExistsError):
        write(path, {"a": 2})
    with pytest.raises(ValueError):
        ensure(path, {"a": 2})
    assert read(path) == {"a": 1}
    assert not list(tmp_path.glob(".checkpoint-*"))


def test_unknown_model_is_not_a_fallback():
    with pytest.raises(KeyError):
        model.settings("typo")
    with pytest.raises(ValueError):
        study.controls("typo", random.Random(1), None)


def test_missing_usage_is_unknown_not_free():
    response = NS(
        usage_metadata=NS(prompt_token_count=5, candidates_token_count=2),
        candidates=[],
        model_version="gemini-2.5-pro",
        prompt_feedback=None,
    )
    report = model.summarize_response(response, "pro-4096")
    assert report["usage_unknown"] and report["estimated_usd"] is None
    response.usage_metadata.thoughts_token_count = 0
    report = model.summarize_response(response, "pro-4096")
    assert not report["usage_unknown"]
    assert report["estimated_usd"] == model.cost("pro-4096", 5, 2)
    assert model.cost("pro-4096", 200001, 2) == (200001 * 2.5 + 30) / 1e6


def test_censoring_and_first_valid_loss_not_clipped():
    rows = [
        {"slot": 1, "valid": False, "loss": None},
        {"slot": 2, "valid": True, "loss": 2.0},
        {"slot": 3, "valid": True, "loss": 0.5},
    ]
    r = summarize(rows, 3, 0.1)
    assert r["curve"] == [1.0, 2.0, 0.5]
    assert r["right_censored"] and r["evaluations_to_target"] == 3
    with pytest.raises(ValueError):
        summarize(rows, 4, 0.1)
    rows[0]["loss"] = 0
    with pytest.raises(ValueError):
        summarize(rows, 3, 0.1)


def test_request_marker_blocks_resampling(tmp_path, monkeypatch):
    directory = tmp_path / "panel/t/610/pro-4096/batches/003"
    write(directory / "request_started.json", {"reservation_usd": 0.5})
    meter = study.Meter(tmp_path, 1.0)
    assert meter.liability == 0.5
    monkeypatch.setattr(study, "generate", lambda *_: pytest.fail("resampled"))
    with pytest.raises(RuntimeError, match="unresolved"):
        meter.call(directory, "pro-4096", "payload", {}, {})


def test_resume_and_short_batch_charge_every_slot(tmp_path, monkeypatch):
    cell = {"target": "t", "seed": 610, "arm": "pro-4096"}
    manifest = {
        "cells": [cell],
        "prefixes": [4],
        "models": {"pro-4096": model.settings("pro-4096")},
        "targets": {"t": {"rates": [1] * 8}},
        "scale": 100,
        "tolerance": 0.1,
        "measurement_fingerprint": "fake",
        "payload_bound": 200000,
    }
    write(tmp_path / "manifest.json", manifest)
    write(tmp_path / "schema.json", {})
    p = random_program(random.Random(4))
    raw = json.dumps({"hypothesis": "test", "candidates": [p], "predictions": []})
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "test")
    calls = []

    def generate(*args):
        calls.append(args)
        return {
            "raw_text": raw,
            "usage_unknown": False,
            "estimated_usd": 0.01,
            "model_version": "gemini-2.5-pro",
        }

    def measured(program, *_):
        if len(evaluated) >= 2:
            assert (
                tmp_path / "panel/t/610/pro-4096/batches/003/response.json"
            ).exists()
        evaluated.append(program)
        if program is None:
            return {"valid": False, "stage": "SCHEMA", "reason": "missing"}, False
        return {
            "valid": True,
            "stage": None,
            "reason": "",
            "cache_id": "test",
            "profile": {"window_rates": [1] * 8},
            "allocation": allocation(program),
            "feedback": {
                "cycles_per_bin": 25000,
                "cycles_without_retirement": [24999] * 8,
                "retired_classes": [
                    {k: int(k == "alu") for k in CLASSES} for _ in range(8)
                ],
            },
            "execution": {},
        }, False

    evaluated = []
    monkeypatch.setattr(study, "generate", generate)
    monkeypatch.setattr(study, "measured", measured)
    meter = study.Meter(tmp_path, 1)
    result = study.search(cell, 4, tmp_path, tmp_path, manifest, meter)
    assert result["valid_slots"] == 3
    assert len(calls) == 1 and len(evaluated) == 4
    result2 = study.search(
        cell, 4, tmp_path, tmp_path, manifest, study.Meter(tmp_path, 1)
    )
    assert result2 == result and len(calls) == 1 and len(evaluated) == 4
