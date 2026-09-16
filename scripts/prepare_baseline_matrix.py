"""Prepare a fresh three-arm panel; never execute or reuse historical caches."""

import argparse
import hashlib
import posixpath
import subprocess
from functools import lru_cache

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, source_inventory
from agcws.pipeline.storage import read, write
from agcws.provenance import file_sha256

DESIGNS = ("aes", "dma", "ibex", "mesh", "redmule")


@lru_cache(maxsize=None)
def pinned_submodules(repository, commit):
    entries = subprocess.check_output(["git", "ls-tree", "-r", commit], cwd=repository, text=True)
    return {line.split("\t")[1]: line.split()[2] for line in entries.splitlines()
            if line.startswith("160000 commit ")}


def committed_file(repository, commit, name, depth=0):
    if depth > 40 or name.startswith("../") or name.startswith("/"):
        raise ValueError("unsafe committed source link")
    for path, pin in pinned_submodules(repository, commit).items():
        if name.startswith(path + "/"):
            return committed_file(repository / path, pin, name[len(path) + 1:], depth + 1)
    entry = subprocess.check_output(["git", "ls-tree", commit, "--", name], cwd=repository, text=True)
    data = subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=repository)
    if entry.startswith("120000 blob "):
        target = posixpath.normpath(posixpath.join(posixpath.dirname(name), data.decode()))
        return committed_file(repository, commit, target, depth + 1)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--development-smoke", action="store_true")
    args = parser.parse_args()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
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
        for name, expected in current.items():
            if name.startswith(".dependencies/"):
                if expected != old["sources"].get(name):
                    raise ValueError(f"generated dependency changed: {name}")
                continue
            committed = committed_file(ROOT, commit, name)
            if hashlib.sha256(committed).hexdigest() != expected:
                raise ValueError(f"commit runtime sources before preparation: {name}")
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
              "runtime_commit": commit,
              "generated_dependencies": "separately content-hashed; unchanged from reference manifest",
              "manifest_sha256": file_sha256(root / "manifest.json"),
              "changed_sources": sorted(changed), "cells": len(targets)*len(seeds)*3,
              "strict_target_feasibility": "not established for every request",
              "witnesses_excluded": True, "paid_execution_authorized": False})
        print(f"Prepared {design}: {len(targets)*len(seeds)*3} cells; execution not started", flush=True)


if __name__ == "__main__":
    main()
