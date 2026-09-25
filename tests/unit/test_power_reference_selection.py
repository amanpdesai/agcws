import gzip
import json

import pytest

from agcws.studies import finalists


def inputs(tmp_path, monkeypatch):
    run, archive = tmp_path / "run", tmp_path / "archive"
    run.mkdir()
    archive.mkdir()
    (archive / finalists.PACK).write_bytes(b"fixture-index")
    spec = {"domain": "aes-temporal", "scale": 1, "tolerance": .05,
            "targets": {"confirmation-A": [1] * 8}}
    (run / "manifest.json").write_text(json.dumps({"spec": spec, "measurement_fingerprint": "frozen"}))
    request = {"id": "A", "witness_case": "confirmation-A", "rates": [1] * 8,
               "qualified": True, "witness_cache_id": "original", "witness_error": .1}
    bank = tmp_path / "bank.json"
    bank.write_text(json.dumps({"domain": "aes-temporal", "calibration": {"scale": 1},
                               "splits": {"confirmation": {"requests": [request]}}}))
    record = {"id": "confirmation-A", "program": {"sequence": []},
              "measurement": {"valid": True, "cache_id": "original", "rates": [.9] * 8}}
    monkeypatch.setattr(finalists, "packed_manifest", lambda _: {"shards": {}})
    monkeypatch.setattr(finalists, "read_selected", lambda _, names: {
        names[0]: gzip.compress(json.dumps(record).encode())})
    return {"run": str(run), "bank": str(bank), "archive": str(archive)}, record, bank


def test_qualification_does_not_imply_strict_activity_solve(tmp_path, monkeypatch):
    entry, _, _ = inputs(tmp_path, monkeypatch)
    plan = finalists.references([entry])
    finalists.verify(plan)
    case = plan["cases"][0]
    assert case["qualification_pass"]
    assert not case["activity_solved"]
    assert case["role"] == "power_reference"


def test_wrong_witness_cannot_be_substituted(tmp_path, monkeypatch):
    entry, record, _ = inputs(tmp_path, monkeypatch)
    record["measurement"]["cache_id"] = "better-result"
    with pytest.raises(ValueError, match="identity differs"):
        finalists.references([entry])


def test_stale_scale_is_rejected(tmp_path, monkeypatch):
    entry, _, bank = inputs(tmp_path, monkeypatch)
    value = json.loads(bank.read_text())
    value["calibration"]["scale"] = 2
    bank.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="domain/scale"):
        finalists.references([entry])


def test_fixed_replay_is_explicitly_not_a_qualified_witness(tmp_path, monkeypatch):
    entry, _, bank = inputs(tmp_path, monkeypatch)
    value = json.loads(bank.read_text())
    value["splits"]["confirmation"]["requests"][0]["qualified"] = False
    bank.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="qualified witness"):
        finalists.references([entry])
    plan = finalists.references([{**entry, "mode": "fixed-replay"}])
    assert plan["cases"][0]["reference_mode"] == "fixed-replay"
    assert not plan["cases"][0]["qualification_pass"]
