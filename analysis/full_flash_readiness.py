"""Read-only final readiness checks; never initialize a provider client."""

import argparse
import hashlib
import math
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.model import MODELS, cost
from agcws.pipeline.storage import read, write


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accounting(root):
    manifest, complete = read(root / "manifest.json"), read(root / "complete.json")
    spec = manifest["spec"]
    if (spec["budget"] != 16 or spec["batch_size"] != 2 or len(spec["targets"]) != 18
            or spec["policies"] != ["flash-4096", "phase-random", "phase-ga"]
            or spec["stop_on_success"] is not False or complete["slots"] != 864 or complete["cells"] != 54):
        raise ValueError("complete matched smoke required")
    known = unknown = 0.0
    feedback = []
    failures = []
    for target in spec["targets"]:
        initial = None
        for arm in spec["policies"]:
            cell = root / "panel" / target / str(spec["seeds"][0]) / arm
            history = [t for p in sorted(cell.glob("batches/*/trials.json")) for t in read(p)]
            if [t["slot"] for t in history] != list(range(1, 17)):
                raise ValueError("slot accounting differs")
            first = [t["program"] for t in history[:2]]
            if initial is not None and first != initial:
                raise ValueError("unmatched initialization")
            initial = first
            for trial in history:
                if trial["valid"]:
                    cached = read(root / "cache" / trial["cache_id"] / "result.json")
                    if not cached["valid"] or cached["profile"]["window_rates"] != trial["rates"]:
                        raise ValueError("measurement/cache mismatch")
                elif trial["loss"] is not None:
                    raise ValueError("invalid slot scored")
            if arm != "flash-4096":
                continue
            if any(t["valid"] for t in history[2:14]):
                feedback.append(target)
            for slot in range(3, 16, 2):
                batch = cell / "batches" / f"{slot:03}"
                response, marker = read(batch / "response.json"), read(batch / "request_started.json")
                error = response.get("api_error")
                if error:
                    if (error.get("type") != "ServerError" or not error.get("message", "").startswith("504 DEADLINE_EXCEEDED.")
                            or not response["usage_unknown"] or response["estimated_usd"] is not None
                            or response["raw_text"] != "" or marker["reservation_usd"] <= 0
                            or any(t["valid"] or t["stage"] != "API" for t in history[slot-1:slot+1])):
                        raise ValueError("unaccounted API failure")
                    unknown += marker["reservation_usd"]
                    failures.append({"target": target, "first_slot": slot, "error": error})
                else:
                    if (response["usage_unknown"] or response["model_version"] != MODELS["flash-4096"]
                            or response["estimated_usd"] != cost("flash-4096", response["tokens_in"], response["tokens_out"])):
                        raise ValueError("unverified model or cost")
                    known += response["estimated_usd"]
    markers = {p.parent for p in root.glob("panel/*/*/*/batches/*/request_started.json")}
    responses = {p.parent for p in root.glob("panel/*/*/*/batches/*/response.json")}
    if len(markers) != 126 or markers != responses:
        raise ValueError("unresolved or extra request")
    if not math.isclose(known+unknown, complete["liability_usd"], abs_tol=1e-9):
        raise ValueError("durable liability differs")
    return {"feedback_targets": feedback, "known_cost_usd": known,
            "unknown_reserved_usd": unknown, "recorded_api_failures": failures, "slots": 864}


def audit():
    records = []
    for name in ("aes", "dma", "mesh", "ibex", "redmule"):
        bank_path = ROOT / f"results/{name}/qualified-bank-v6.json"
        bank = read(bank_path)
        reference = ROOT / f"out/{name}-transport-bridge-v1/reference"
        current = verify_inputs(ROOT, reference)
        if not bank["target_bank_qualified"] or bank["calibration"]["measurement_fingerprint"] != current["measurement_fingerprint"]:
            raise ValueError("unadmitted current bank")
        for split in ("development", "confirmation"):
            requests = bank["splits"][split]["requests"]
            if (len(requests) != 9 or sum(r["control"] for r in requests) != 1
                    or any(not r["qualified"] or not 0 <= r["witness_error"] <= .1
                           or (not r["control"] and r["constant_floor"] <= .12) for r in requests)):
                raise ValueError("target admission gate differs")
        version = 5 if name in ("aes", "dma") else 4
        smoke = ROOT / f"out/{name}-bank-smoke-v{version}/run"
        if version == 5:
            strict = runpy.run_path(ROOT / "analysis/bank_smoke.py")["analyze"](smoke)
            if strict != read(smoke / "audit.json"):
                raise ValueError("smoke audit changed")
        else:
            context = runpy.run_path(ROOT / "analysis/smoke_context_replay.py")["audit"](smoke, reference, bank_path)
            if context != read(ROOT / f"results/{name}/context-replay-v6.json") or not context["byte_identical_context"]:
                raise ValueError("historical context not equivalent")
            strict = read(smoke / "audit.json")
        record = accounting(smoke)
        missing = set(read(smoke / "manifest.json")["spec"]["targets"]) - set(record["feedback_targets"])
        delivery_receipt = None
        if missing:
            diagnostic = ROOT / f"out/{name}-late-feedback-v1-final"
            config, completed = read(diagnostic / "config.json"), read(diagnostic / "complete.json")
            verify_inputs(ROOT, diagnostic)
            frozen = read(diagnostic / "freeze.json")
            if (frozen != {"manifest": digest(diagnostic / "manifest.json"),
                           "config": digest(diagnostic / "config.json"),
                           "driver": digest(ROOT / "analysis/late_feedback.py"),
                           "protocol": digest(ROOT / "docs/LATE_FEEDBACK_V1.md")}
                    or frozen["manifest"] != digest(smoke / "manifest.json")):
                raise ValueError("delivery provenance changed")
            if ({c["target"] for c in config["cases"]} != missing or not completed["delivered"]
                    or completed["charged_slots"] != 2*len(missing)):
                raise ValueError("missing feedback delivery")
            design, manifest = backend(bank["domain"]), read(smoke / "manifest.json")
            for case in config["cases"]:
                original = smoke / "panel" / case["target"] / "8503/flash-4096"
                history = [t for p in sorted(original.glob("batches/*/trials.json")) for t in read(p)]
                if case["history"] != history:
                    raise ValueError("delivery history differs from measured smoke")
                batch = diagnostic / "panel" / case["target"] / "8503/flash-4096/batches/017"
                payload = design.payload(case["history"], {"profile": manifest["spec"]["targets"][case["target"]],
                                         "scale": manifest["spec"]["scale"], "tolerance": .1}, 2)
                response = read(batch / "response.json")
                if (payload != read(batch / "input.json")["payload"] or response.get("api_error")
                        or response["usage_unknown"] or response["model_version"] != MODELS["flash-4096"]
                        or design.decode(response["raw_text"], 2) != read(batch / "decoded.json")):
                    raise ValueError("delivery payload/response mismatch")
                trials = read(batch / "trials.json")
                if [t["slot"] for t in trials] != [17, 18] or any(not t["valid"] and t["loss"] is not None for t in trials):
                    raise ValueError("delivery slot accounting differs")
                if response["estimated_usd"] != cost("flash-4096", response["tokens_in"], response["tokens_out"]):
                    raise ValueError("delivery cost differs")
                for trial in trials:
                    if trial["valid"]:
                        cached = read(diagnostic / "cache" / trial["cache_id"] / "result.json")
                        if not cached["valid"] or cached["profile"]["window_rates"] != trial["rates"]:
                            raise ValueError("delivery measurement differs")
            delivery_receipt = completed
        planned = ROOT / f"out/{name}-full-flash-v1"
        full = verify_inputs(ROOT, planned / "run")
        expected = runpy.run_path(ROOT / "scripts/prepare_full_flash.py")["config"](bank, current)
        freeze = read(planned / "freeze.json")
        if (full["spec"] != expected or freeze["config_sha256"] != digest(planned / "config.json")
                or freeze["manifest_sha256"] != digest(planned / "run/manifest.json")
                or freeze["protocol_sha256"] != digest(ROOT / "docs/FULL_FLASH_V1.md")
                or freeze["bank_sha256"] != digest(bank_path) or freeze["launch_authorized"]
                or (planned / "run/panel").exists()):
            raise ValueError("full-study freeze changed or execution began")
        records.append({"design": name, "bank_sha256": digest(bank_path), "qualified_requests": 18,
                        "strict_smoke_targets_ready": strict["targets_ready"], "smoke_version": version,
                        "accounting": record, "late_feedback": delivery_receipt,
                        "operational_feedback_targets": 18, "full_plan_sha256": freeze["manifest_sha256"]})
    return {"ready_for_launch_approval": True, "launch_authorized": False,
            "scope": "operational engineering readiness, not model performance or zero-error certification",
            "designs": records, "qualified_requests": 90, "feedback_requests": 90,
            "paper_cells_prepared": 1350, "full_study_calls_made": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, audit())
