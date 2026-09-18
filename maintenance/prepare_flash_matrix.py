"""Prepare matched Flash-only manifests. Never simulate or contact a provider."""

import argparse
import copy
import json
import subprocess
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline import engine
from agcws.pipeline.model import settings
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import read, write
from agcws.provenance import file_sha256

DESIGNS = ("aes", "dma", "ibex", "mesh", "redmule")
ARM = "flash-lite-medium"
PROVIDER_ONLY = {"src/agcws/pipeline/model.py", "src/agcws/pipeline/schedule_backend.py"}
CONFIG_CHANGES = {"name", "policies", "cost_ceiling_usd"}


def matched(reference, candidate, arm=ARM):
    for field in set(reference["spec"]) | set(candidate["spec"]):
        if field not in CONFIG_CHANGES and reference["spec"].get(field) != candidate["spec"].get(field):
            raise ValueError(f"task contract changed: {field}")
    for field in ("schema", "runtime"):
        if reference[field] != candidate[field]:
            raise ValueError(f"{field} changed")
    changed = {p for p in reference["sources"].keys() | candidate["sources"].keys()
               if reference["sources"].get(p) != candidate["sources"].get(p)}
    if changed - PROVIDER_ONLY:
        raise ValueError(f"non-provider sources changed: {sorted(changed - PROVIDER_ONLY)}")
    if candidate["spec"]["policies"] != [arm] or candidate["models"] != {arm: settings(arm)}:
        raise ValueError("unexpected model arm or settings")
    return {p: {"baseline": reference["sources"][p], "flash": candidate["sources"][p]}
            for p in sorted(changed)}


def prepare(repo, destination, evidence, ceiling):
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    for path in PROVIDER_ONLY:
        committed = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo)
        if committed != (repo / path).read_bytes():
            raise ValueError(f"commit reviewed provider code before freezing: {path}")
    if destination.exists() or evidence.exists():
        raise FileExistsError("use new execution and evidence directories")
    receipts = []
    for design in DESIGNS:
        reference_path = repo / "results" / design / "baselines-model-v1-plan/manifest.json"
        reference = read(reference_path)
        spec = copy.deepcopy(reference["spec"])
        spec.update(name=f"{design}-flash-lite-matched-v1", policies=[ARM], cost_ceiling_usd=ceiling)
        validate(spec)
        plan = evidence / design
        write(plan / "config.json", spec)
        run_root = destination / design
        candidate = engine.prepare(repo, plan / "config.json", run_root)
        changes = matched(reference, candidate)
        engine.verify_inputs(repo, run_root)
        write(plan / "manifest.json", candidate)
        receipts.append({"design": design, "cells": len(spec["targets"]) * len(spec["seeds"]),
                         "baseline_manifest_sha256": file_sha256(reference_path),
                         "manifest_sha256": file_sha256(run_root / "manifest.json"),
                         "provider_only_source_changes": changes,
                         "schema_runtime_and_task_contract_equal": True,
                         "measurement_fingerprint_equal": reference["measurement_fingerprint"] ==
                         candidate["measurement_fingerprint"],
                         "run_directory": str(run_root)})
    receipt = {"runtime_commit": commit, "model": settings(ARM), "designs": receipts,
               "cells": sum(r["cells"] for r in receipts), "paid_calls": 0,
               "execution_authorized": False, "proposed_total_ceiling_usd": 5 * ceiling,
               "baseline_reuse": "same tasks/runtime/schema; only reviewed provider registration differs",
               "fingerprint_note": "whole-source hashes change with model registration; no cache reuse",
               "live_smoke_scope": "prior AES two-call migration smoke; no new live calls in preparation"}
    write(evidence / "readiness.json", receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--ceiling-per-design", type=float, default=120)
    args = parser.parse_args()
    print(json.dumps(prepare(ROOT, args.directory.resolve(), args.evidence.resolve(),
                             args.ceiling_per_design), indent=2))


if __name__ == "__main__":
    main()
