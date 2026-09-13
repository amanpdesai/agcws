"""Freeze requested vectors and emit ordinary CPU witness-search configurations."""

import argparse
import hashlib
import itertools
import json
import statistics
from pathlib import Path

from agcws.pipeline.calibration import report
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import SHAPES, diagnostics, distance, mean_matched_requests, requests


def fixed_work_requests(low, high, mean, split):
    if split not in ("development", "confirmation") or not low < mean < high:
        raise ValueError("explicit split and nondegenerate calibrated mean required")
    shapes = dict(SHAPES)
    if split == "development":
        shapes.update(activation=(0, 0, 0, 1, 1, 1, 1, 1),
                      deactivation=(1, 1, 1, 0, 0, 0, 0, 0),
                      burst=(0, 0, 1, 1, 0, 0, 0, 0),
                      quiet_interval=(1, 1, 0, 0, 0, 1, 1, 1),
                      alternating=(1, 0, 1, 0, 1, 0, 1, 0),
                      ramp=(0, .14, .29, .43, .57, .71, .86, 1),
                      rise_fall=(0, .5, 1, 1, .5, 0, 0, 0),
                      irregular=(1, 0, .5, 0, 1, 0, .5, 0))
    result = []
    for name, shape in shapes.items():
        if name == "flat_control":
            rates = [mean]*8
        else:
            center = statistics.mean(shape)
            amplitude = min((mean-low)/(center-min(shape)), (high-mean)/(max(shape)-center))
            amplitude *= .9 if split == "development" else 1.0
            rates = [mean+amplitude*(value-center) for value in shape]
        result.append({"id": name, "split": split, "rates": rates,
                       "control": name == "flat_control", "qualified": False,
                       **diagnostics(rates, high-low)})
    return result


def prepare(calibration_root, destination, version=1):
    if version not in (1, 2):
        raise ValueError("known qualification version required")
    calibration = report(calibration_root)
    if calibration["status"] != "calibrated":
        raise ValueError("target planning requires a completed nondegenerate calibration")
    manifest = read(calibration_root / "manifest.json")
    domain = manifest["spec"]["domain"]
    if version == 2 and domain not in ("aes-temporal", "dma-temporal"):
        raise ValueError("v2 fixed-work procedure applies only to AES/DMA")
    destination.mkdir(parents=True, exist_ok=False)
    bank = {"procedure": f"docs/TARGET_QUALIFICATION_V{version}.md", "calibration": calibration,
            "calibration_manifest_sha256": hashlib.sha256((calibration_root / "manifest.json").read_bytes()).hexdigest(),
            "qualified": False, "splits": {}}
    seeds = (7300, 7400) if version == 1 else (7800, 7900)
    for split, seed in zip(("development", "confirmation"), seeds, strict=True):
        if version == 2:
            requested = fixed_work_requests(calibration["low"], calibration["high"],
                                            calibration["median_window_mean"], split)
        elif domain in ("aes-temporal", "dma-temporal"):
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
        spec = {**manifest["spec"], "name": f"target-witness-v{version}-{domain}-{split}",
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
    parser.add_argument("--version", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    print(json.dumps(prepare(args.calibration, args.destination, args.version), indent=2))


if __name__ == "__main__":
    main()
