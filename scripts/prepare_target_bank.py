"""Freeze requested vectors and emit ordinary CPU witness-search configurations."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

from agcws.pipeline.calibration import report
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import distance, mean_matched_requests, requests


def prepare(calibration_root, destination):
    calibration = report(calibration_root)
    if calibration["status"] != "calibrated":
        raise ValueError("target planning requires a completed nondegenerate calibration")
    manifest = read(calibration_root / "manifest.json")
    domain = manifest["spec"]["domain"]
    destination.mkdir(parents=True, exist_ok=False)
    bank = {"procedure": "docs/TARGET_QUALIFICATION_V1.md", "calibration": calibration,
            "calibration_manifest_sha256": hashlib.sha256((calibration_root / "manifest.json").read_bytes()).hexdigest(),
            "qualified": False, "splits": {}}
    for split, seed in (("development", 7300), ("confirmation", 7400)):
        if domain in ("aes-temporal", "dma-temporal"):
            requested = mean_matched_requests(calibration["low"], calibration["high"],
                                             calibration["median_window_mean"], split=split)
        else:
            requested = requests(calibration["low"], calibration["high"], split=split)
        for request in requested:
            request["necessary_floor_gate"] = request["control"] or request["constant_floor"] > 0.12
        pairwise = [{"left": a["id"], "right": b["id"],
                     "distance": distance(a["rates"], b["rates"], calibration["scale"])}
                    for a, b in itertools.combinations(requested, 2)]
        bank["splits"][split] = {"requests": requested, "pairwise_distances": pairwise}
        spec = {**manifest["spec"], "name": f"target-witness-v1-{domain}-{split}",
                "targets": {r["id"]: r["rates"] for r in requested}, "seeds": [seed],
                "policies": ["phase-random", "phase-ga"], "budget": 256, "batch_size": 2,
                "scale": calibration["scale"], "tolerance": 0.1, "max_workers": 18,
                "image": manifest["runtime"]["image_id"], "stop_on_success": False}
        write(destination / f"{split}.json", validate(spec))
    write(destination / "requested_bank.json", bank)
    return {"domain": domain, "splits": {name: {
        "requests": len(part["requests"]),
        "necessary_floor_failures": [r["id"] for r in part["requests"] if not r["necessary_floor_gate"]],
        "qualified": 0} for name, part in bank["splits"].items()}, "executed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.calibration, args.destination), indent=2))


if __name__ == "__main__":
    main()
