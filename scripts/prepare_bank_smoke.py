"""Prepare a six-slot Flash/random/GA smoke for every admitted target, never run it."""

import argparse
import hashlib
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import read, write


def config(bank, manifest):
    if (bank.get("target_bank_qualified") is not True
            or bank["domain"] != manifest["spec"]["domain"]
            or bank["calibration"]["measurement_fingerprint"] != manifest["measurement_fingerprint"]):
        raise ValueError("qualified bank must match current measurement")
    if set(bank["splits"]) != {"development", "confirmation"}:
        raise ValueError("both target splits required")
    targets = {}
    for split, part in bank["splits"].items():
        requests = part["requests"]
        if len(requests) != 9 or sum(r["control"] for r in requests) != 1:
            raise ValueError("eight nonflat targets and a control required")
        for request in requests:
            if not request["qualified"] or not 0 <= request["witness_error"] <= .1:
                raise ValueError("unqualified witness")
            if not request["control"] and request["constant_floor"] <= .12:
                raise ValueError("nonflat floor fails")
            targets[f"{split}-{request['id']}"] = request["rates"]
    if len(targets) != 18:
        raise ValueError("duplicate target identifiers")
    return validate({**manifest["spec"], "name": f"{bank['domain']}-bank-smoke-v2",
                     "targets": targets, "seeds": [8500], "budget": 6, "batch_size": 2,
                     "policies": ["flash-4096", "phase-random", "phase-ga"],
                     "scale": bank["calibration"]["scale"], "tolerance": .1,
                     "max_workers": 18, "provider_workers": 3, "cost_ceiling_usd": 5.0,
                     "stop_on_success": False, "image": manifest["runtime"]["image_id"]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    spec = config(read(args.bank), verify_inputs(ROOT, args.reference))
    args.directory.mkdir(parents=True, exist_ok=False)
    write(args.directory / "config.json", spec)
    write(args.directory / "qualification.json", {"bank_sha256": hashlib.sha256(args.bank.read_bytes()).hexdigest(),
          "scope": "qualification receipt, not model input; smoke seeds excluded from paper inference"})
    prepare(ROOT, args.directory / "config.json", args.directory / "run")
    print({"cells": 54, "slots": 324, "max_model_calls": 36, "ceiling_usd": 5, "executed": False})
