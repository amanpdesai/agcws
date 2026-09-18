"""Audit frozen full-panel inputs and completed smokes without provider calls."""

import argparse
import json
import threading
from collections import Counter
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline import engine
from agcws.pipeline.metrics import error, max_bin_error
from agcws.pipeline.storage import read, write
from agcws.provenance import file_sha256
from analysis.publish_flash_matrix import ReplayMeter
from maintenance.prepare_flash_matrix import DESIGNS, matched
from maintenance.resume_budget import ReconciledMeter
from maintenance.strong_matrix import ARM, support_hashes


def no_evaluation(*args):
    raise RuntimeError("readiness audit cannot simulate a missing trial")


def audit(full, smoke):
    rows = []
    for design in DESIGNS:
        root, check = full / design, smoke / design
        manifest = engine.verify_inputs(ROOT, root)
        for directory in (root, check):
            contract = read(directory / "launch-contract.json")
            if contract["support_sha256"] != support_hashes():
                raise ValueError("launch/accounting code differs")
            if contract["manifest_sha256"] != file_sha256(directory / "manifest.json"):
                raise ValueError("manifest differs")
        reference = read(ROOT / f"results/{design}/baselines-model-v1-plan/manifest.json")
        matched(reference, manifest, ARM)
        matched(read(ROOT / f"results/flash_lite_matched_v1_plan/{design}/manifest.json"), manifest, ARM)
        if (root / "panel").exists() or (root / "complete.json").exists():
            raise ValueError("full study has already started")
        sm = engine.verify_inputs(ROOT, check)
        if sm["models"] != manifest["models"] or sm["runtime"] != manifest["runtime"]:
            raise ValueError("smoke model/runtime mismatch")
        if list(check.glob("failure-*.json")):
            raise ValueError("smoke infrastructure failure retained; investigate before launch")
        cell = check / "panel/confirmation-alternating/9100" / ARM
        responses, trials = [], []
        for index in (1, 3, 5):
            batch = cell / "batches" / f"{index:03d}"
            for name in ("proposals.json", "trials.json"):
                if not (batch / name).exists():
                    raise ValueError(f"missing smoke record: {batch / name}")
            trials.extend(read(batch / "trials.json"))
            if index > 1:
                for name in ("response.json", "input.json", "decoded.json", "request_started.json"):
                    if not (batch / name).exists():
                        raise ValueError(f"missing provider record: {batch / name}")
                responses.append(read(batch / "response.json"))
        replay = ReplayMeter()
        replay.halted = threading.Event()
        summary = engine.cell(check, sm, "confirmation-alternating", 9100, ARM,
                              replay, no_evaluation)
        if len(trials) != 6 or len(responses) != 2:
            raise ValueError("incomplete smoke")
        spec = sm["spec"]
        target = spec["targets"]["confirmation-alternating"]
        for trial in trials:
            if trial["valid"]:
                if (abs(trial["loss"] - error(trial["rates"], target, spec["scale"])) > 1e-12
                        or abs(trial["max_bin_error"] - max_bin_error(
                            trial["rates"], target, spec["scale"])) > 1e-12):
                    raise ValueError("smoke metric arithmetic differs")
            elif trial["loss"] is not None or trial["max_bin_error"] is not None:
                raise ValueError("invalid smoke proposal received a score")
        if any(r.get("api_error") or r["model_version"] != "gemini-3.8-flash" for r in responses):
            raise ValueError("provider failure or model mismatch")
        if any("MAX_TOKENS" in reason for r in responses for reason in r["finish_reasons"]):
            raise ValueError("truncated smoke response")
        if not all(any(t["valid"] for t in trials[start:start + 2]) for start in (2, 4)):
            raise ValueError("smoke requires a valid generated workload in each feedback round")
        completed = read(check / "complete.json")
        liability = ReconciledMeter(check, 2).liability
        if completed["summaries"] != [summary] or abs(completed["liability_usd"] - liability) > 1e-9:
            raise ValueError("saved completion/accounting mismatch")
        rows.append({"design": design, "full_cells": 90, "smoke_slots": 6,
                     "valid_model_proposals": sum(t["valid"] for t in trials[2:]),
                     "invalid_stages": dict(Counter(t["stage"] for t in trials if not t["valid"])),
                     "provider_calls": 2, "model_versions": [r["model_version"] for r in responses],
                     "finish_reasons": [r["finish_reasons"] for r in responses],
                     "known_usage_estimate_usd": sum(r["estimated_usd"] or 0 for r in responses),
                     "unknown_usage_calls": sum(r["usage_unknown"] for r in responses),
                     "conservative_liability_usd": liability,
                     "best_generated_max_bin_error": min(t["max_bin_error"] for t in trials[2:] if t["valid"]),
                     "full_manifest_sha256": file_sha256(root / "manifest.json"),
                     "feedback_payload_replay_verified": True})
    return {"operational_ready": True, "full_matrix_started": False,
            "scope": "compatibility readiness, not a performance or universal-success guarantee",
            "cells": 450, "designs": rows, "paid_calls_in_audit": 0,
            "checker_sha256": file_sha256(Path(__file__)),
            "full_launch_authorization_required": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", type=Path, required=True)
    parser.add_argument("--smoke", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.full, args.smoke)
    write(args.output, result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
