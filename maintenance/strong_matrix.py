"""Prepare or explicitly execute the matched Gemini 3.8 arm; never auto-launch."""

import argparse
import copy
import json
import subprocess
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline import engine
from agcws.pipeline.model import cost, settings
from agcws.pipeline.policies.dispatch import Policy
from agcws.pipeline.storage import ensure, read, write
from agcws.provenance import file_sha256
from maintenance.prepare_flash_matrix import DESIGNS, PROVIDER_ONLY, matched
from maintenance.resume_budget import VERSION, ReconciledMeter

ARM = "strong-medium"
SUPPORT = ("maintenance/strong_matrix.py", "maintenance/resume_budget.py",
           "maintenance/prepare_flash_matrix.py")


def support_hashes():
    return {p: file_sha256(ROOT / p) for p in SUPPORT}


def prepare(directory, evidence, smoke=False):
    if directory.exists() or evidence.exists():
        raise FileExistsError("new execution and evidence roots required")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    for path in (*SUPPORT, *PROVIDER_ONLY):
        committed = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)
        if committed != (ROOT / path).read_bytes():
            raise ValueError(f"commit reviewed code before freezing: {path}")
    receipts = []
    for design in DESIGNS:
        reference_path = ROOT / f"results/{design}/baselines-model-v1-plan/manifest.json"
        reference = read(reference_path)
        spec = copy.deepcopy(reference["spec"])
        spec.update(name=f"{design}-strong-{'smoke' if smoke else 'matched'}-v1",
                    policies=[ARM], cost_ceiling_usd=2 if smoke else 120)
        if smoke:
            spec.update(targets={"confirmation-alternating": spec["targets"]["confirmation-alternating"]},
                        seeds=[9100], budget=6, max_workers=1, stop_on_success=False)
        config = evidence / design / "config.json"
        write(config, spec)
        root = directory / design
        candidate = engine.prepare(ROOT, config, root)
        if smoke:
            comparable = copy.deepcopy(candidate)
            for field in ("targets", "seeds", "budget", "max_workers", "stop_on_success"):
                comparable["spec"][field] = reference["spec"][field]
        else:
            comparable = candidate
        changes = matched(reference, comparable, ARM)
        engine.verify_inputs(ROOT, root)
        for seed in spec["seeds"]:
            kwargs = dict(spec=spec, target=next(iter(spec["targets"].values())),
                          schema=candidate["schema"], meter=None)
            if (Policy(ARM, seed, **kwargs).propose([], root, {}) !=
                    Policy("phase-random", seed, **kwargs).propose([], root, {})):
                raise ValueError("shared initialization differs")
        freeze = {"manifest_sha256": file_sha256(root / "manifest.json"),
                  "support_sha256": support_hashes(), "accounting": VERSION,
                  "scope": "smoke" if smoke else "full-matched",
                  "full_matrix_launch_authorized": False}
        ensure(root / "launch-contract.json", freeze)
        write(evidence / design / "manifest.json", candidate)
        write(evidence / design / "launch-contract.json", freeze)
        receipts.append({"design": design, "cells": len(spec["targets"]) * len(spec["seeds"]),
                         "baseline_manifest_sha256": file_sha256(reference_path),
                         "manifest_sha256": freeze["manifest_sha256"],
                         "provider_only_source_changes": changes,
                         "runtime_schema_and_shared_initializations_match": True})
    result = {"runtime_commit": commit, "model": settings(ARM), "designs": receipts,
              "cells": sum(r["cells"] for r in receipts), "paid_calls_during_preparation": 0,
              "full_matrix_launch_authorized": False, "accounting": VERSION,
              "scope": "smoke" if smoke else "full-matched",
              "ceiling_per_design_usd": 2 if smoke else 120,
              "maximum_calls": 10 if smoke else 28350,
              "full_input_output_reservation_per_call_usd": cost(ARM, 200000, 8192)}
    write(evidence / "preparation.json", result)
    return result


def execute(root, allow_paid=False):
    if not allow_paid:
        raise ValueError("explicit --allow-paid required")
    contract = read(root / "launch-contract.json")
    if contract["support_sha256"] != support_hashes():
        raise ValueError("frozen launch/accounting code changed")
    if contract["manifest_sha256"] != file_sha256(root / "manifest.json"):
        raise ValueError("frozen manifest changed")
    manifest = engine.verify_inputs(ROOT, root)
    if manifest["spec"]["policies"] != [ARM] or contract["accounting"] != VERSION:
        raise ValueError("unexpected arm or accounting version")
    engine.Meter = ReconciledMeter
    engine.run(ROOT, root, allow_paid=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run"))
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--allow-paid", action="store_true")
    args = parser.parse_args()
    if args.action == "prepare":
        if args.evidence is None or args.allow_paid:
            parser.error("prepare requires --evidence and never accepts --allow-paid")
        print(json.dumps(prepare(args.directory.resolve(), args.evidence.resolve(), args.smoke)))
    else:
        if args.smoke or args.evidence:
            parser.error("run uses the frozen launch contract, not prepare options")
        execute(args.directory.resolve(), args.allow_paid)


if __name__ == "__main__":
    main()
