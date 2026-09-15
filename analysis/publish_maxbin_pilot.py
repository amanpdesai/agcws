"""Audit and archive the budget-censored all-bin pilot without inventing completion."""

import gzip
import hashlib
import json

from agcws.config import ROOT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.metrics import error, max_bin_error, summarize
from agcws.pipeline.storage import read, write


def main():
    root = ROOT / "out/ibex-maxbin-pilot-v1"
    manifest = verify_inputs(ROOT, root)
    spec = manifest["spec"]
    if spec["success_metric"] != "max-bin" or spec["tolerance"] != .05:
        raise ValueError("wrong pilot criterion")
    cells, liability, calls = [], 0.0, 0
    for target, rates in spec["targets"].items():
        for seed in spec["seeds"]:
            for arm in spec["policies"]:
                cell = root / "panel" / target / str(seed) / arm
                trials = []
                for batch in sorted((cell / "batches").iterdir()):
                    path = batch / "trials.json"
                    if not path.exists():
                        continue
                    rows, proposals = read(path), read(batch / "proposals.json")
                    if len(rows) != len(proposals) or any(
                        any(t.get(k) != v for k, v in p.items())
                        for t, p in zip(rows, proposals, strict=True)
                    ):
                        raise ValueError("proposal/trial mismatch")
                    trials.extend(rows)
                if [t["slot"] for t in trials] != list(range(1, len(trials)+1)):
                    raise ValueError("noncontiguous charged slots")
                for t in trials:
                    if t["valid"]:
                        cached = read(root / "cache" / t["cache_id"] / "result.json")
                        if cached["profile"]["window_rates"] != t["rates"]:
                            raise ValueError("measured rates differ")
                        if (error(t["rates"], rates, spec["scale"]) != t["loss"]
                                or max_bin_error(t["rates"], rates, spec["scale"]) != t["max_bin_error"]):
                            raise ValueError("metric mismatch")
                    elif t["loss"] is not None or t["max_bin_error"] is not None:
                        raise ValueError("invalid scored attempt")
                done = cell / "complete.json"
                summary = None
                if done.exists():
                    summary = summarize(trials, 128, .05, stop_on_success=True, success_metric="max-bin")
                    if any(read(done)[k] != v for k, v in summary.items()):
                        raise ValueError("terminal summary differs")
                valid = [t for t in trials if t["valid"]]
                best = min(valid, key=lambda t: t["max_bin_error"]) if valid else None
                cells.append({"target": target, "seed": seed, "arm": arm,
                    "charged_slots": len(trials), "valid_slots": len(valid),
                    "state": "solved" if summary and summary["solved"] else "budget_exhausted" if summary else "cost_interrupted",
                    "summary": summary, "best_max_bin_error": best["max_bin_error"] if best else None,
                    "best_slot": best["slot"] if best else None, "best_rates": best["rates"] if best else None})
    for started in root.glob("panel/*/*/*/batches/*/request_started.json"):
        calls += 1
        info = read(started.parent / "response.json")
        liability += read(started)["reservation_usd"] if info["usage_unknown"] else info["estimated_usd"]
    if liability > spec["cost_ceiling_usd"]:
        raise ValueError("liability exceeded cap")
    result = {"scope": "exploratory pilot, one exposed target/two seeds; incomplete panel, no comparative inference",
              "success_metric": "max-bin", "tolerance": .05, "cells": cells,
              "estimated_liability_usd": liability, "calls": calls,
              "failures": [read(p) for p in sorted(root.glob("failure-*.json"))],
              "full_panel_complete": (root / "complete.json").exists()}
    destination = ROOT / "results/ibex/maxbin-pilot-v1"
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "summary.json", result)
    paths = [root / "manifest.json", *root.glob("failure-*.json"),
             *root.glob("panel/**/*.json"), *root.glob("cache/*/result.json")]
    bundle = {}
    for path in sorted(paths):
        raw = path.read_bytes()
        bundle[str(path.relative_to(root))] = {"sha256": hashlib.sha256(raw).hexdigest(), "text": raw.decode()}
    encoded = json.dumps(bundle, sort_keys=True).encode()
    packed = gzip.compress(encoded, mtime=0)
    if gzip.decompress(packed) != encoded:
        raise ValueError("archive roundtrip differs")
    with (destination / "evidence.json.gz").open("xb") as stream:
        stream.write(packed)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
