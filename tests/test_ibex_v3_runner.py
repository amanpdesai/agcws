import hashlib
import json
import random

import pytest

from experiments.ibex_temporal_v3 import search
from experiments.ibex_temporal_v3.agent import prompt
from experiments.ibex_temporal_v3.program import random_program


@pytest.mark.parametrize(
    "policy", ["agent-base", "agent-context", "agent-correction", "agent-combined"]
)
def test_runner_charges_short_batches_and_preserves_tokens(
    tmp_path, monkeypatch, policy
):
    class FakeAgent:
        last_usage = {"tokens_in": 3, "tokens_out": 5}
        last_diagnostics = {}

        @classmethod
        def from_vertex(cls, *args, **kwargs):
            return cls()

        def propose(self, *args):
            return [{}]

    source = policy in ("agent-context", "agent-combined")
    correction = policy in ("agent-correction", "agent-combined")
    manifest = {
        "sources": {},
        "targets": {"t": {"rates": [1] * 8}},
        "seeds": [600],
        "policies": [policy],
        "scale": 1,
        "tolerance": 0.1,
        "budget": 4,
        "model": "fake",
        "input_rate": 0.3,
        "output_rate": 2.5,
        "measurement_fingerprint": "test",
        "context_root": str(tmp_path),
        "context_sha256": "test",
        "context_payload_sha256": search.key({"test_context": True}),
        "prompts": {
            policy: hashlib.sha256(prompt(source, correction).encode()).hexdigest()
        },
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    monkeypatch.setattr(search, "TemporalAgent", FakeAgent)
    monkeypatch.setattr(search, "verify_runtime", lambda *_: None)
    monkeypatch.setattr(search, "load_context", lambda *args: {"test_context": True})
    monkeypatch.setattr(
        search,
        "measured",
        lambda *args: ({"valid": False, "stage": "SCHEMA", "reason": "test"}, False),
    )
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "test")
    search.search(path, tmp_path, "t", policy, 600)
    output = tmp_path / "panel/t/seed-600" / policy
    rows = [
        json.loads(line) for line in (output / "trials.jsonl").read_text().splitlines()
    ]
    summary = json.loads((output / "summary.json").read_text())
    assert len(rows) == 4
    assert summary["auc"] == 3 and summary["right_censored"]
    assert summary["evaluations_to_target"] == 4
    assert sum(t["tokens_in"] for t in rows) == 3
    assert sum(t["tokens_out"] for t in rows) == 5
    assert (output / "source_context.json").exists() == source


def test_runtime_guard_rejects_source_drift_before_starting_tools(tmp_path):
    path = tmp_path / "controller.py"
    path.write_text("changed")
    with pytest.raises(ValueError, match="changed frozen"):
        search.verify_runtime({"sources": {str(path): "wrong"}}, tmp_path)


def test_integral_encodings_share_cache_without_resimulation(tmp_path):
    item = random_program(random.Random(3))
    floating = json.loads(json.dumps(item), parse_int=float)
    identifier = search.key({"program": item, "measurement": "frozen"})
    cache = tmp_path / "cache" / identifier
    cache.mkdir(parents=True)
    record = {"valid": True, "cache_id": identifier, "fixture": True}
    (cache / "result.json").write_text(json.dumps(record))
    assert search.measured(item, tmp_path, "frozen") == (record, True)
    assert search.measured(floating, tmp_path, "frozen") == (record, True)


def test_schema_rejection_has_precise_path_without_simulation(tmp_path):
    item = random_program(random.Random(3))
    item["segments"][0]["weight"] = 1.5
    record, hit = search.measured(item, tmp_path, "frozen")
    assert not hit and not record["valid"]
    assert record["schema_path"] == ["segments", 0, "weight"]
    assert not (tmp_path / "cache").exists()
