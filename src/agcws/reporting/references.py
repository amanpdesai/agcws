"""Verify reference construction and qualification against final power records."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from agcws.evidence.power import load as load_power
from agcws.reporting.metrics import key
from agcws.reporting.reference_audit import digest, maximum_error, validity

DESIGNS = ("aes", "dma", "ibex", "mesh", "redmule")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_join(case, measurement):
    activity = measurement["activity"]
    for field in ("program", "rates", "target_rates", "scale", "max_bin_error"):
        assert activity[field] == case[field], (case["target"], field)
    assert activity["target"] == case["target"]
    assert activity["activity_solved"] is True


def verify(root):
    count = 0
    for design in DESIGNS:
        base = root / "results" / design
        _, records = load_power(root, design)
        index = json.loads((base / "tasks/references/index.json").read_bytes())
        assert len(index["references"]) == 8
        for path, expected in index.get("inputs", {}).items():
            assert sha((root / path).read_bytes()) == expected, path
        task_dir = base / "tasks/references"
        cases = {}
        if task_dir.exists():
            cases = {c["target"]: c for c in json.loads((task_dir / "bank.json").read_bytes())["cases"]}
            evidence = json.loads(gzip.decompress((task_dir / "evidence.json.gz").read_bytes()))
            for entry in evidence.values():
                assert sha(entry["text"].encode()) == entry["sha256"]
            task = json.loads(evidence["frozen-task.json"]["text"])
            for target, c in cases.items():
                m = json.loads(evidence[target + "/measurement.json"]["text"])
                assert digest(c["program"]) == c["program_sha256"]
                assert digest(c["measurement_manifest"]) == c["manifest_sha256"]
                assert m["cache_id"] == key({"program": c["program"], "measurement": c["measurement_manifest"]["measurement_fingerprint"]})
                assert validity(design, c["program"], m) == []
                assert m["profile"]["window_rates"] == c["rates"]
                assert c["target_rates"] == task["targets"][target] and c["scale"] == task["scale"]
                assert maximum_error(c["rates"], c["target_rates"], c["scale"]) == c["max_bin_error"] <= task["tolerance"] == .05
                for n, source in enumerate(c["functional_sources"]):
                    assert evidence[target + f"/functional-{n}.json"]["sha256"] == source["sha256"]
                if c["source"]["kind"] == "fresh-independent-reference":
                    for name in ("request", "measurement", "qualification"):
                        assert evidence[target + "/" + name + ".json"]["sha256"] == c["source"][name + "_sha256"]
                    request = json.loads(evidence[target + "/request.json"]["text"])
                    assert request["program"] == c["program"] and request["manifest"] == c["measurement_manifest"]
                else:
                    row = json.loads(evidence[target + "/original-record.json"]["text"])
                    assert digest(row) == c["source"]["record_sha256"]
                    assert row["program"] == c["program"] and row["measurement"] == m
            proof = json.loads(gzip.decompress((base / "power/validation/references.json.gz").read_bytes()))
            assert set(proof) == set(cases) == set(index["references"])
            for target, item in proof.items():
                assert item["measurement_sha256"] == index["references"][target]["sha256"]
                native = records[index["references"][target]["case_id"]]
                for name, entry in item["files"].items():
                    assert sha(entry["text"].encode()) == entry["sha256"]
                    if name.startswith("power/"):
                        assert entry["source_sha256"] == native["power"]["artifact_sha256"][name.split("/")[-1]]
        for target, entry in index["references"].items():
            measurement = records[entry["case_id"]]
            assert measurement["activity"]["target"] == target
            if cases:
                check_join(cases[target], measurement)
            count += 1
    return {"verified_native_measurements": count}


if __name__ == '__main__':
    print(json.dumps(verify(Path.cwd()), sort_keys=True))
