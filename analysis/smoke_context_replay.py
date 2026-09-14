"""Compare frozen smoke payloads with the current controller without model calls."""

import argparse
import hashlib
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.model import MODELS, settings
from agcws.pipeline.provider_schema import provenance
from agcws.pipeline.storage import read, write


def audit(root, reference, bank_path):
    current = verify_inputs(ROOT, reference)
    old = read(root / "manifest.json")
    spec, bank = old["spec"], read(bank_path)
    expected_targets = {f"{split}-{r['id']}": r['rates'] for split, part in bank['splits'].items()
                        for r in part['requests']}
    if (spec["budget"] != 16 or spec["batch_size"] != 2 or spec["seeds"] != [8502]
            or spec["policies"] != ["flash-4096", "phase-random", "phase-ga"]
            or spec["stop_on_success"] is not False or len(expected_targets) != 18):
        raise ValueError("complete frozen v4 smoke settings required")
    if (not bank["target_bank_qualified"] or current["measurement_fingerprint"] != bank["calibration"]["measurement_fingerprint"]
            or spec["domain"] != bank["domain"] or spec["targets"] != expected_targets
            or spec["scale"] != bank["calibration"]["scale"]):
        raise ValueError("admitted bank/current reference differs from smoke targets")
    if old["models"] != {a: settings(a) for a in spec["policies"] if a in MODELS}:
        raise ValueError("model configuration changed")
    complete = read(root / "complete.json")
    if complete["cells"] != 54 or complete["slots"] != 864:
        raise ValueError("complete sixteen-slot smoke required")
    design, calls, mismatches = backend(spec["domain"]), 0, []
    for target, rates in spec["targets"].items():
        cell = root / "panel" / target / str(spec["seeds"][0]) / "flash-4096"
        history = [t for path in sorted(cell.glob("batches/*/trials.json")) for t in read(path)]
        if [r["slot"] for r in history] != list(range(1, 17)):
            raise ValueError("all sixteen charged slots required")
        for offset in range(2, 16, 2):
            batch = cell / "batches" / f"{offset+1:03}"
            response = read(batch / "response.json")
            payload = design.payload(history[:offset], {"profile": rates, "scale": spec["scale"],
                                      "tolerance": spec["tolerance"]}, 2)
            checks = {"payload": payload == read(batch / "input.json")["payload"],
                      "schema": provenance(design.schema(2)) == response["schema_provenance"],
                      "parsing": design.decode(response["raw_text"], 2) == read(batch / "decoded.json")}
            calls += 1
            if not all(checks.values()):
                mismatches.append({"target": target, "first_slot": offset+1, "checks": checks})
    if calls != 126:
        raise ValueError("all 126 frozen model requests required")
    return {"domain": spec["domain"], "calls_checked": calls, "byte_identical_context": not mismatches,
            "mismatches": mismatches, "old_manifest_sha256": hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest(),
            "current_reference_sha256": hashlib.sha256((reference / "manifest.json").read_bytes()).hexdigest(),
            "bank_sha256": hashlib.sha256(bank_path.read_bytes()).hexdigest(),
            "scope": "payload/schema/parsing compatibility only; historical errors and strict readiness unchanged",
            "model_calls": 0, "full_study_ready": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, audit(args.directory, args.reference, args.bank))
