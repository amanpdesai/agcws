import gzip
import hashlib
import json

import pytest

from agcws.reporting.reference_audit import bundle, maximum_error, validity


def measurement(work):
    return {"valid": True, "profile": {"activity_contract": "known-bit-activity-v2",
                                      "useful_work": work}}


def test_maximum_bin_gate_does_not_accept_rmse_only_match():
    # RMS is .0283 but the failed bin is .08.
    assert maximum_error([.08] + [0.] * 7, [0.] * 8, 1.) == .08


@pytest.mark.parametrize("rates,scale", [([0.] * 7, 1), ([float("nan")] * 8, 1),
                                        ([0.] * 8, 0), ([-1.] * 8, 1)])
def test_bad_metric_inputs(rates, scale):
    with pytest.raises(ValueError):
        maximum_error(rates, [0.] * 8, scale)


def test_mesh_sources_distribute_packets_not_multiply_them():
    program = {"phases": [{"packets": 64, "sources": [0, 1, 2, 3]}]}
    assert validity("mesh", program, measurement(64)) == []
    assert validity("mesh", program, measurement(256))


@pytest.mark.parametrize("design,work", [("aes", 64), ("dma", 4096)])
def test_repeat_expansion_and_exact_idle_contract(design, work):
    p = {"sequence": [{"op": "repeat", "count": 2, "body": [
        {"op": "work", "units": 32}, {"op": "wait", "cycles": 3000}]}]}
    assert validity(design, p, measurement(work)) == []
    p["sequence"][0]["body"][1]["cycles"] = 2999
    assert validity(design, p, measurement(work))


def test_invalid_functional_result_cannot_qualify():
    p = {"size": 4, "phases": [{"jobs": 16}]}
    m = measurement(1024)
    assert validity("redmule", p, m) == []
    m["valid"] = False
    assert validity("redmule", p, m)


def test_ibex_requires_deadline_and_body_work():
    m = measurement(None)
    m.update(allocation=[4096], feedback={"body_completed_before_deadline": True})
    assert validity("ibex", {}, m) == []
    m["feedback"]["body_completed_before_deadline"] = False
    assert validity("ibex", {}, m)


def test_bundle_rejects_changed_payload(tmp_path):
    path = tmp_path / "bundle.gz"
    original = '{"valid":true}'
    record = {"x": {"text": original, "sha256": hashlib.sha256(original.encode()).hexdigest()}}
    with gzip.open(path, "wt") as stream:
        json.dump(record, stream)
    assert bundle(path)[0]["x"]["valid"] is True
    record["x"]["text"] = '{"valid":false}'
    with gzip.open(path, "wt") as stream:
        json.dump(record, stream)
    with pytest.raises(ValueError, match="checksum"):
        bundle(path)
