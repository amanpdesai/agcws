"""Measure a frozen random-only calibration concurrently; the runner still charges every slot."""

import argparse
import concurrent.futures
import random
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.storage import ensure


def cases(spec, design):
    if (spec["policies"] != ["random"] or spec["stop_on_success"] is not False
            or spec["targets"] != {"calibration_only": [0.0] * 8}):
        raise ValueError("only independent random calibration can be premeasured")
    result = []
    for seed in spec["seeds"]:
        rng = random.Random(seed)
        result.extend({"seed": seed, "slot": slot, "program": design.random(rng)}
                      for slot in range(1, spec["budget"] + 1))
    return result


def run(root, workers):
    if not 1 <= workers <= 32:
        raise ValueError("workers must be in 1..32")
    manifest = verify_inputs(ROOT, root)
    design = backend(manifest["spec"]["domain"])
    if not hasattr(design, "measured"):
        raise ValueError("schedule backend required")
    proposals = cases(manifest["spec"], design)
    ensure(root / "prewarm-plan.json", {"cases": proposals, "workers": workers,
                                      "measurement_fingerprint": manifest["measurement_fingerprint"]})

    def evaluate(case):
        measured, hit = design.measured(case["program"], root, manifest)
        row = {**case, "measurement": measured, "cache_hit": hit}
        print({"seed": case["seed"], "slot": case["slot"], "valid": measured["valid"]}, flush=True)
        return row

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(evaluate, proposals))
    ensure(root / "prewarm-result.json", {"records": rows})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=18)
    args = parser.parse_args()
    run(args.directory, args.workers)
