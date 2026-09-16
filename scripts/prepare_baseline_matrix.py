"""Prepare a fresh three-arm panel; never execute or reuse historical caches."""

import argparse

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, source_inventory
from agcws.pipeline.storage import read, write
from agcws.provenance import file_sha256

DESIGNS = ("aes", "dma", "ibex", "mesh", "redmule")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--development-smoke", action="store_true")
    args = parser.parse_args()
    split = "development" if args.development_smoke else "confirmation"
    version = "baselines-model-v1-dev" if args.development_smoke else "baselines-model-v1"
    allowed = {f"src/agcws/pipeline/{p}" for p in
               ("engine.py", "metrics.py", "spec.py", "policies/dispatch.py", "policies/controls.py",
                "policies/temporal_model.py", "retention.py", "schedule_backend.py", "ibex/cache.py")}
    for design in DESIGNS:
        path = ROOT / "results" / design / ("bit-refinement-v1" if design == "mesh" else "bit-activity-v2") / "bank.json"
        bank = read(path)
        old = read(ROOT / "out/bit-activity-v2" / design / "reference/manifest.json")
        current = source_inventory(ROOT, old["spec"]["domain"])
        changed = {p for p in set(current) | set(old["sources"])
                   if current.get(p) != old["sources"].get(p)}
        if changed != allowed:
            raise ValueError(f"unexpected runtime changes for {design}: {changed}")
        targets = {split+"-"+t["id"]: t["rates"] for t in bank["splits"][split]["requests"]}
        if len(targets) != 9 or not bank["task_bank_qualified"]:
            raise ValueError("nine unchanged RMSE-qualified requests required")
        if args.development_smoke:
            targets = {"development-alternating": targets["development-alternating"]}
        seeds = [9300] if args.development_smoke else list(range(9100, 9110))
        spec = {**old["spec"], "name": f"{design}-{version}",
                "targets": targets, "seeds": seeds,
                "policies": ["phase-random", "phase-ga", "phase-model"],
                "budget": 12 if args.development_smoke else 128,
                "batch_size": 2, "scale": bank["calibration"]["scale"],
                "tolerance": .05, "success_metric": "max-bin", "stop_on_success": True,
                "max_workers": 3 if args.development_smoke else 18,
                "provider_workers": 1, "cost_ceiling_usd": 1.0}
        destination = ROOT / "results" / design / f"{version}-plan"
        destination.mkdir(parents=True, exist_ok=False)
        write(destination / "config.json", spec)
        root = ROOT / "out" / version / design
        manifest = prepare(ROOT, destination / "config.json", root)
        if manifest["models"] or manifest["runtime"] != old["runtime"]:
            raise ValueError("CPU-only unchanged runtime required")
        write(destination / "manifest.json", manifest)
        write(destination / "freeze.json", {"bank_sha256": file_sha256(path),
              "manifest_sha256": file_sha256(root / "manifest.json"),
              "changed_sources": sorted(changed), "cells": len(targets)*len(seeds)*3,
              "strict_target_feasibility": "not established for every request",
              "witnesses_excluded": True, "paid_execution_authorized": False})
        print(f"Prepared {design}: {len(targets)*len(seeds)*3} cells; execution not started", flush=True)


if __name__ == "__main__":
    main()
