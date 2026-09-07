import json
import random

from experiments.ibex_temporal_v3.program import random_program
from experiments.ibex_temporal_v4 import contract_study as study


def test_run_preserves_failures_and_never_retries(tmp_path, monkeypatch):
    calls = [{"name": arm, "arm": arm} for arm in ("original", "contract")]
    manifest = {"calls": calls, "settings": {"model": "fake"}}
    study.write(tmp_path / "manifest.json", manifest)
    study.write(tmp_path / "schema.json", {})
    (tmp_path / "inputs").mkdir()
    for call in calls:
        (tmp_path / "inputs" / f"{call['name']}.json").write_text("payload\n")
    monkeypatch.setattr(study, "verify", lambda _: manifest)
    monkeypatch.setattr(
        study.subprocess,
        "check_output",
        lambda *_: (tmp_path / "manifest.json").read_bytes(),
    )
    monkeypatch.setattr(study.config, "_load_dotenv", lambda: None)
    monkeypatch.setenv("AGCWS_GCP_PROJECT", "fake")
    monkeypatch.setattr(study, "client", lambda _: None)
    requested = []

    def request(*args):
        requested.append(args)
        if len(requested) == 1:
            raise ValueError("test API error")
        return {
            "raw_text": json.dumps(
                {
                    "hypothesis": "test",
                    "candidates": [
                        random_program(random.Random(3)),
                        random_program(random.Random(4)),
                    ],
                }
            ),
            "usage_unknown": False,
            "tokens_in": 10,
            "tokens_out": 20,
            "est_cost_usd": 0.01,
        }

    monkeypatch.setattr(study, "request", request)
    study.run(tmp_path)
    result = json.loads((tmp_path / "aggregate.json").read_text())
    assert len(requested) == 2
    assert result["arms"]["original"]["requested_slots"] == 2
    assert result["arms"]["original"]["api_errors"] == 1
    assert result["arms"]["contract"]["schema_valid"] == 2
    assert result["ready"]
