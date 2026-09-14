"""One metered delivery of a terminal smoke candidate; never resample the smoke."""

import argparse
import fcntl
import hashlib
import json
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.meter import Meter
from agcws.pipeline.model import MODELS
from agcws.pipeline.policies.dispatch import Policy
from agcws.pipeline.storage import ensure, read, write


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eligible(history):
    if [t["slot"] for t in history] != list(range(1, 17)):
        raise ValueError("complete sixteen-slot history required")
    return not any(t["valid"] for t in history[2:14]) and any(t["valid"] for t in history[14:])


def plan(source, destination):
    manifest = verify_inputs(ROOT, source)
    if manifest["spec"]["seeds"] != [8503] or manifest["spec"]["domain"] not in ("aes-temporal", "dma-temporal"):
        raise ValueError("AES/DMA v5 smoke required")
    audit = runpy.run_path(ROOT / "analysis/bank_smoke.py")["analyze"](source)
    cases = []
    for row in audit["records"]:
        if row["measured_generated_feedback"]:
            continue
        cell = source / "panel" / row["target"] / "8503/flash-4096"
        history = [t for p in sorted(cell.glob("batches/*/trials.json")) for t in read(p)]
        if not eligible(history):
            raise ValueError(f"no terminal generated candidate: {row['target']}")
        cases.append({"target": row["target"], "history": history})
    if not cases:
        raise ValueError("no late-feedback diagnostic needed")
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "manifest.json", manifest)
    write(destination / "config.json", {"source": str(source.resolve()), "cases": cases,
                                        "cost_ceiling_usd": 2.0})
    write(destination / "freeze.json", {"manifest": digest(destination / "manifest.json"),
                                       "config": digest(destination / "config.json"),
                                       "driver": digest(Path(__file__)),
                                       "protocol": digest(ROOT / "docs/LATE_FEEDBACK_V1.md")})
    return {"cases": len(cases), "new_slots": 2*len(cases), "executed": False}


def run(root):
    with (root / "runner.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return execute(root)


def execute(root):
    frozen = read(root / "freeze.json")
    if frozen != {"manifest": digest(root / "manifest.json"), "config": digest(root / "config.json"),
                  "driver": digest(Path(__file__)), "protocol": digest(ROOT / "docs/LATE_FEEDBACK_V1.md")}:
        raise ValueError("diagnostic inputs changed")
    manifest, config = verify_inputs(ROOT, root), read(root / "config.json")
    if digest(Path(config["source"]) / "manifest.json") != frozen["manifest"]:
        raise ValueError("source smoke manifest changed")
    design = backend(manifest["spec"]["domain"])
    meter = Meter(root, config["cost_ceiling_usd"], provider_workers=1)
    records = []
    for case in config["cases"]:
        target, history = case["target"], case["history"]
        if not eligible(history):
            raise ValueError("ineligible diagnostic case")
        spec = {**manifest["spec"], "budget": 18}
        policy = Policy("flash-4096", 8503, spec, spec["targets"][target], manifest["schema"], meter)
        batch = root / "panel" / target / "8503/flash-4096/batches/017"
        payload = json.loads(design.payload(history, {"profile": spec["targets"][target],
                             "scale": spec["scale"], "tolerance": spec["tolerance"]}, 2))
        shown = payload["history"]
        if not any(t["valid"] and any(all(r.get(k) == t.get(k) for k in
                       ("slot", "program", "valid", "rates", "residual", "loss")) for r in shown)
                   for t in history[14:]):
            raise ValueError("terminal measurement not visible in payload")
        proposals = policy.propose(history, batch, {"source_manifest": frozen["manifest"],
                                     "target": target, "seed": 8503, "first_slot": 17,
                                     "scope": "late-feedback-delivery-v1"})
        if [p["slot"] for p in proposals] != [17, 18]:
            raise ValueError("exactly two additional slots required")
        ensure(batch / "proposals.json", proposals)
        trials = []
        saved = read(batch / "trials.json") if (batch / "trials.json").exists() else None
        if saved is not None and (len(saved) != 2 or any(
                any(t.get(k) != v for k, v in p.items())
                for t, p in zip(saved, proposals, strict=True))):
            raise ValueError("saved diagnostic trials differ from proposals")
        for p in ([] if saved is not None else proposals):
            trial = design.evaluate({"submitted": p["program"], "prediction": p.get("prediction"),
                                     "prediction_error": p.get("prediction_error")}, p["slot"], history,
                                    {**manifest, "scale": spec["scale"], "target_rates": spec["targets"][target]},
                                    root, "flash-4096")
            trial.update(p)
            if p.get("api_error"):
                trial.update(stage="API", reason=p["api_error"]["message"])
            if not trial["valid"] and trial["loss"] is not None:
                raise ValueError("invalid diagnostic proposal scored")
            trials.append(trial)
        trials = saved if saved is not None else trials
        ensure(batch / "trials.json", trials)
        response = read(batch / "response.json")
        records.append({"target": target, "delivered": not response.get("api_error")
                        and not response["usage_unknown"] and response["model_version"] == MODELS["flash-4096"],
                        "known_cost_usd": response["estimated_usd"],
                        "valid_new_slots": sum(t["valid"] for t in trials)})
    result = {"kind": "late-feedback-delivery-v1", "charged_slots": 2*len(records),
              "records": records, "delivered": all(r["delivered"] for r in records),
              "liability_usd": meter.liability, "strict_smoke_status_changed": False}
    ensure(root / "complete.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "run"))
    parser.add_argument("--source", type=Path)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--allow-paid", action="store_true")
    args = parser.parse_args()
    if args.action == "plan":
        if args.source is None:
            parser.error("plan requires source")
        print(plan(args.source, args.directory))
    else:
        if not args.allow_paid:
            parser.error("run requires --allow-paid")
        print(run(args.directory))
