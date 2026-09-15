"""Freeze the authorized five-design CPU baseline matrix without witness leakage."""

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, source_inventory
from agcws.pipeline.storage import read, write
from agcws.provenance import file_sha256

DESIGNS = ("aes", "dma", "ibex", "mesh", "redmule")


def main():
    allowed = {f"src/agcws/pipeline/{p}" for p in
               ("engine.py", "metrics.py", "spec.py", "policies/dispatch.py")}
    for design in DESIGNS:
        path = ROOT / "results" / design / ("bit-refinement-v1" if design == "mesh" else "bit-activity-v2") / "bank.json"
        bank = read(path)
        old = read(ROOT / "out/bit-activity-v2" / design / "reference/manifest.json")
        current = source_inventory(ROOT, old["spec"]["domain"])
        changed = {p for p in set(current) | set(old["sources"])
                   if current.get(p) != old["sources"].get(p)}
        if changed != allowed:
            raise ValueError(f"unexpected runtime changes for {design}: {changed}")
        targets = {"confirmation-"+t["id"]: t["rates"] for t in bank["splits"]["confirmation"]["requests"]}
        if len(targets) != 9 or not bank["task_bank_qualified"]:
            raise ValueError("nine unchanged RMSE-qualified requests required")
        spec = {**old["spec"], "name": f"{design}-baselines-maxbin-v1",
                "targets": targets, "seeds": list(range(9100, 9110)),
                "policies": ["phase-random", "phase-ga"], "budget": 128,
                "batch_size": 2, "scale": bank["calibration"]["scale"],
                "tolerance": .05, "success_metric": "max-bin", "stop_on_success": True,
                "max_workers": 18, "provider_workers": 1, "cost_ceiling_usd": 1.0}
        destination = ROOT / "results" / design / "baselines-maxbin-v1-plan"
        destination.mkdir(parents=True, exist_ok=False)
        write(destination / "config.json", spec)
        root = ROOT / "out/baselines-maxbin-v1" / design
        manifest = prepare(ROOT, destination / "config.json", root)
        if manifest["models"] or manifest["runtime"] != old["runtime"]:
            raise ValueError("CPU-only unchanged runtime required")
        write(destination / "manifest.json", manifest)
        write(destination / "freeze.json", {"bank_sha256": file_sha256(path),
              "manifest_sha256": file_sha256(root / "manifest.json"),
              "changed_sources": sorted(changed), "cells": 180,
              "strict_target_feasibility": "not established for every request",
              "witnesses_excluded": True, "paid_execution_authorized": False})
        print(f"Prepared {design}: 180 cells, 23040 maximum slots", flush=True)


if __name__ == "__main__":
    main()
