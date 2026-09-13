"""Prepare a bounded Flash/baseline smoke from an exactly replayed control."""

import argparse
import hashlib
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import qualify


def prepare(reference, qualification, destination):
    m = verify_inputs(ROOT, reference)
    witness_root = qualification.parents[2]
    witness_manifest = read(witness_root / "manifest.json")
    result = read(qualification)
    if witness_manifest["measurement"] != m or result["id"] != "confirmation-flat_control":
        raise ValueError("matching replayed confirmation control required")
    case = next(c for c in witness_manifest["cases"] if c["id"] == result["id"])
    request = case["request"]
    scale = witness_manifest["bank"]["calibration"]["scale"]
    admission = qualify(request, result["measurement"], scale=scale, tolerance=.1, nonflat_margin=.02)
    cached = read(witness_root / "cache" / result["measurement"]["cache_id"] / "result.json")
    if not request["control"] or not admission["qualified"] or cached != result["measurement"]:
        raise ValueError("control lacks a valid cached measured witness")
    spec = {**m["spec"], "name": f"flash-control-smoke-v1-{m['spec']['domain']}",
            "targets": {"flat_control": request["rates"]}, "seeds": [8200],
            "policies": ["flash-4096", "phase-random", "phase-ga"], "budget": 6,
            "batch_size": 2, "scale": scale, "tolerance": .1, "max_workers": 3,
            "provider_workers": 1, "cost_ceiling_usd": 1.0, "stop_on_success": False,
            "image": m["runtime"]["image_id"]}
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "config.json", validate(spec))
    write(destination / "qualification.json", {
        "scope": "qualification receipt, not model input", "admission": admission,
        "measurement_fingerprint": m["measurement_fingerprint"],
        "witness_record_sha256": hashlib.sha256(qualification.read_bytes()).hexdigest(),
        "witness_manifest_sha256": hashlib.sha256((witness_root / "manifest.json").read_bytes()).hexdigest()})
    return {"domain": m["spec"]["domain"], "paid_calls_maximum": 2, "ceiling_usd": 1.0}


if __name__ == "__main__":
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.reference.resolve(), args.qualification.resolve(), args.destination.resolve())))
