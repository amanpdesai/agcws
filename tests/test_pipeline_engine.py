import copy
import gzip
import json
import random
import threading
from pathlib import Path

import pytest

from agcws.pipeline import engine
from agcws.pipeline.__main__ import main
from agcws.pipeline.ibex.native_schema import serving_schema
from agcws.pipeline.ibex.program import allocation, canonical, random_program
from agcws.pipeline.meter import Meter
from agcws.pipeline.metrics import error
from agcws.pipeline.model import MODELS
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import read, write


def specification(arm="random", budget=8, batch=2):
    spec = read(Path("configs/study.example.json"))
    spec.update(policies=[arm], budget=budget, batch_size=batch)
    return validate(spec)


def manifest(root, arm="random", budget=8, batch=2):
    spec = specification(arm, budget, batch)
    result = {"spec": spec, "schema": serving_schema(batch, True)}
    write(root / "manifest.json", result)
    return result


def evaluate(proposal, slot, history, manifest, root, arm):
    submitted = proposal["submitted"]
    p = canonical(submitted) if submitted is not None else None
    return {
        "valid": p is not None,
        "loss": error([50.0] * 8, manifest["target_rates"], manifest["scale"]) if p else None,
        "rates": [50.0] * 8 if p else None,
        "reason": "" if p else "missing",
        "residual": [0.1] * 8 if p else None,
        "allocation": allocation(p) if p else None,
        "canonical_program": p,
        "stage": None if p else "SCHEMA",
        "feedback": None,
        "execution": None,
        "prediction": proposal["prediction"],
        "prediction_error": proposal["prediction_error"],
    }


@pytest.mark.parametrize(
    "arm,batch",
    [
        ("random", 2),
        ("phase-random", 2),
        ("phase-ga", 2),
        ("gest-batch2", 4),
        ("gest-pool4", 4),
        ("ridge-screen", 4),
    ],
)
def test_shared_budget_resume_and_filtered_accounting(tmp_path, arm, batch):
    m = manifest(tmp_path, arm, batch=batch)
    meter = Meter(tmp_path, 1)
    first = engine.cell(tmp_path, m, "example", 0, arm, meter, evaluate)

    def forbidden(*args):
        raise AssertionError("completed measurements must not be repeated")

    second = engine.cell(tmp_path, m, "example", 0, arm, meter, forbidden)
    assert first == second
    assert first["budget"] == 8
    assert first["evaluations_to_target"] == 8 and first["right_censored"]
    assert first["filtered"] == (2 if arm == "ridge-screen" else 0)
    assert first["valid_slots"] + first["filtered"] == 8


def test_short_model_batch_charges_every_requested_slot(tmp_path):
    m = manifest(tmp_path, "pro-4096", 4)

    class FakeMeter:
        halted = threading.Event()
        calls = 0

        def call(self, *args):
            self.calls += 1
            return {
                "model_version": MODELS["pro-4096"],
                "raw_text": json.dumps(
                    {
                        "hypothesis": "test",
                        "candidates": [random_program(random.Random(9))],
                    }
                ),
            }

    meter = FakeMeter()
    result = engine.cell(tmp_path, m, "example", 0, "pro-4096", meter, evaluate)
    assert meter.calls == 1 and result["budget"] == 4 and result["valid_slots"] == 3
    rows = read(tmp_path / "panel/example/0/pro-4096/batches/003/trials.json")
    assert rows[1]["stage"] == "SCHEMA" and rows[1]["loss"] is None


def test_infrastructure_failure_does_not_become_a_trial(tmp_path):
    m = manifest(tmp_path)

    def broken(*args):
        raise RuntimeError("infrastructure")

    with pytest.raises(RuntimeError, match="infrastructure"):
        engine.cell(tmp_path, m, "example", 0, "random", Meter(tmp_path, 1), broken)
    assert not list(tmp_path.rglob("trials.json"))
    assert not list(tmp_path.rglob("complete.json"))


def test_invalid_score_fails_closed(tmp_path):
    m = manifest(tmp_path)

    def broken(*args):
        return {"valid": False, "loss": 0.0}

    with pytest.raises(ValueError, match="invalid workload received"):
        engine.cell(tmp_path, m, "example", 0, "random", Meter(tmp_path, 1), broken)


def test_explicit_execution_and_paid_guards(tmp_path, monkeypatch):
    with pytest.raises(SystemExit) as e:
        main(["run", "--directory", str(tmp_path)])
    assert e.value.code == 2
    monkeypatch.setattr(engine, "verify_inputs", lambda *_: {"spec": specification("pro-4096")})
    with pytest.raises(ValueError, match="allow-paid"):
        engine.run(tmp_path, tmp_path)
    assert not list(tmp_path.iterdir())


def test_export_roundtrip_and_tamper(tmp_path):
    root = tmp_path / "run"
    destination = tmp_path / "export"
    write(root / "complete.json", {"cells": 1})
    write(root / "panel/example/0/random/batches/001/trials.json", [{"valid": True}])
    (root / "huge.vcd").write_text("scratch")
    engine.export(root, destination)
    assert engine.verify_export(destination)["files"] == 2
    assert (root / "huge.vcd").exists()
    (destination / "complete.json.gz").write_bytes(gzip.compress(b"{}"))
    with pytest.raises(ValueError, match="inventory differs"):
        engine.verify_export(destination)


@pytest.mark.parametrize(
    "field,value",
    [
        ("budget", 1),
        ("scale", 0),
        ("targets", {"../bad": [1] * 8}),
        ("policies", ["unknown"]),
        ("binary", ""),
        ("image", ""),
    ],
)
def test_invalid_spec_is_rejected(field, value):
    spec = copy.deepcopy(specification())
    spec[field] = value
    with pytest.raises(ValueError):
        validate(spec)


def test_unresolved_provider_request_is_never_resampled(tmp_path, monkeypatch):
    directory = tmp_path / "panel/example/0/pro-4096/batches/003"
    write(directory / "request_started.json", {"reservation_usd": 0.5})
    meter = Meter(tmp_path, 1)
    assert meter.liability == 0.5

    def forbidden(*args):
        raise AssertionError("must not call provider")

    monkeypatch.setattr("agcws.pipeline.meter.generate", forbidden)
    with pytest.raises(RuntimeError, match="unresolved request"):
        meter.call(directory, "pro-4096", "test", {}, {})


def test_meter_replays_response_and_preserves_unknown_cost(tmp_path, monkeypatch):
    directory = tmp_path / "panel/example/0/pro-4096/batches/003"
    identity = {"target": "example"}
    write(directory / "request_started.json", {"reservation_usd": 0.5})
    response = {
        "identity": identity,
        "usage_unknown": True,
        "estimated_usd": None,
        "raw_text": "",
    }
    write(directory / "response.json", response)
    meter = Meter(tmp_path, 1)
    assert meter.liability == 0.5
    assert meter.call(directory, "pro-4096", "test", {}, identity) == response
    with pytest.raises(ValueError, match="identity differs"):
        meter.call(directory, "pro-4096", "test", {}, {"other": 1})


def test_full_runner_completion_and_resume_use_same_cells(tmp_path, monkeypatch):
    m = manifest(tmp_path)
    monkeypatch.setattr(engine, "verify_inputs", lambda *_: m)
    original = engine.cell
    monkeypatch.setattr(engine, "cell", lambda *args: original(*args, evaluator=evaluate))
    engine.run(tmp_path, tmp_path)
    assert engine.status(tmp_path)["completed_slots"] == 8
    completed = read(tmp_path / "complete.json")
    engine.run(tmp_path, tmp_path)
    assert read(tmp_path / "complete.json") == completed


def test_preparation_pins_binary_source_inventory_and_image(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "docker").mkdir(parents=True)
    (repo / "docker/run.sh").write_text("container entry")
    (repo / "src/agcws").mkdir(parents=True)
    (repo / "src/agcws/example.py").write_text("VALUE = 1\n")
    runtime = repo / "third_party/ibex/examples/sw/simple_system/common"
    runtime.mkdir(parents=True)
    (runtime / "link.ld").write_text("runtime")
    binary = tmp_path / "simulator"
    binary.write_text("binary fixture")
    spec = specification()
    spec["binary"] = str(binary)
    spec_path = tmp_path / "spec.json"
    write(spec_path, spec)
    monkeypatch.setattr(
        engine.subprocess, "check_output", lambda *args, **kwargs: "sha256:fixture\n"
    )
    root = tmp_path / "prepared"
    prepared = engine.prepare(repo, spec_path, root)
    binary.write_text("upstream binary changed")
    assert engine.verify_inputs(repo, root) == prepared
    (runtime / "link.ld").write_text("changed")
    with pytest.raises(ValueError, match="inventory changed"):
        engine.verify_inputs(repo, root)


def test_source_inventory_detects_added_source_files(tmp_path, monkeypatch):
    (tmp_path / "src/agcws").mkdir(parents=True)
    (tmp_path / "docker").mkdir()
    (tmp_path / "docker/run.sh").write_text("fixture")
    before = engine.source_inventory(tmp_path)
    (tmp_path / "src/agcws/new.py").write_text("VALUE = 1")
    assert engine.source_inventory(tmp_path) != before
