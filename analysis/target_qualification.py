"""Audit completed CPU witnesses against frozen requests without moving targets."""

import argparse
import hashlib
import json
from pathlib import Path

from agcws.pipeline.metrics import error
from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import qualify


def analyze(root, bank_path, split):
    bank = read(bank_path)
    manifest = read(root / "manifest.json")
    spec = manifest["spec"]
    requested = bank["splits"][split]["requests"]
    procedure = bank.get("procedure", "docs/TARGET_QUALIFICATION_V1.md")
    if procedure == "docs/TARGET_QUALIFICATION_V1.md":
        seed = 7300 if split == "development" else 7400
    elif procedure == "docs/TARGET_QUALIFICATION_V2.md" and spec["domain"] in ("aes-temporal", "dma-temporal"):
        seed = 7800 if split == "development" else 7900
    else:
        raise ValueError("unknown witness qualification procedure")
    if manifest["measurement_fingerprint"] != bank["calibration"]["measurement_fingerprint"]:
        raise ValueError("measurement contract changed after calibration")
    if (spec["targets"] != {r["id"]: r["rates"] for r in requested}
            or spec["scale"] != bank["calibration"]["scale"] or spec["tolerance"] != 0.1
            or spec["budget"] != 256 or spec["batch_size"] != 2
            or spec["seeds"] != [seed]
            or spec["policies"] != ["phase-random", "phase-ga"] or spec.get("stop_on_success") is not False
            or spec["domain"] != bank["calibration"]["domain"]):
        raise ValueError("witness run differs from frozen request procedure")
    if read(root / "complete.json")["slots"] != 9*2*256:
        raise ValueError("incomplete witness panel")
    results = []
    for request in requested:
        valid = []
        arms = {}
        for arm in spec["policies"]:
            cell = root / "panel" / request["id"] / str(spec["seeds"][0]) / arm
            trials = [t for path in sorted((cell / "batches").glob("*/trials.json")) for t in read(path)]
            if [t["slot"] for t in trials] != list(range(1, 257)):
                raise ValueError("missing or repeated proposal slots")
            rejections = {}
            first_hit = None
            for trial in trials:
                if trial["valid"] is True:
                    cached = read(root / "cache" / trial["cache_id"] / "result.json")
                    if cached["valid"] is not True or cached["profile"]["window_rates"] != trial["rates"]:
                        raise ValueError("trial differs from cached measurement")
                    loss = error(trial["rates"], request["rates"], spec["scale"])
                    if loss != trial["loss"]:
                        raise ValueError("stored loss differs from target calculation")
                    valid.append((loss, arm, trial["slot"], trial))
                    if first_hit is None and loss <= spec["tolerance"]:
                        first_hit = trial["slot"]
                else:
                    if trial["loss"] is not None:
                        raise ValueError("invalid proposal has a score")
                    stage = trial["stage"]
                    rejections[stage] = rejections.get(stage, 0) + 1
            arms[arm] = {"proposals": 256, "invalid_by_stage": rejections,
                         "first_hit": first_hit, "right_censored": first_hit is None}
        selected = min(valid, key=lambda item: item[:3]) if valid else None
        witness = selected[3] if selected else {"valid": False}
        result = {"id": request["id"], "control": request["control"], "arms": arms,
                  **qualify(request, witness, scale=spec["scale"], tolerance=0.1, nonflat_margin=0.02)}
        if selected:
            result["witness"] = {"policy": selected[1], "slot": selected[2], "cache_id": witness["cache_id"],
                                 "program": witness["program"], "rates": witness["rates"]}
        results.append(result)
    return {"scope": "target qualification; witnesses must not be supplied to search policies",
            "domain": spec["domain"], "split": split,
            "request_bank_sha256": hashlib.sha256(bank_path.read_bytes()).hexdigest(),
            "run_manifest_sha256": hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest(),
            "qualified_nonflat": sum(r["qualified"] and not r["control"] for r in results),
            "qualified_controls": sum(r["qualified"] and r["control"] for r in results),
            "requests": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--split", choices=("development", "confirmation"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.directory, args.bank, args.split)
    write(args.output, result)
    print(json.dumps({key: result[key] for key in ("domain", "split", "qualified_nonflat", "qualified_controls")}))


if __name__ == "__main__":
    main()
