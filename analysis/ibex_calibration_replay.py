"""Replay the full original Ibex corpus, including all three rejected workloads."""

import argparse
import concurrent.futures
import hashlib
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.calibration import report
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.ibex.cache import measured
from agcws.pipeline.storage import ensure, read, write


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def comparable(result):
    profile = result.get("profile")
    return {"valid": result["valid"], "stage": result["stage"],
            "profile": None if profile is None else {k: v for k, v in profile.items() if k != "extraction_s"},
            "allocation": result.get("allocation"), "feedback": result.get("feedback"),
            "execution": result.get("execution")}


def plan(corpus, bank_path, root):
    bank = read(bank_path)
    if report(corpus) != bank["calibration"]:
        raise ValueError("original corpus does not reproduce normalization")
    rows = [t for p in sorted((corpus / "panel").rglob("trials.json")) for t in read(p)]
    cases = []
    for index, row in enumerate(rows):
        cached = read(corpus / "cache" / row["cache_id"] / "result.json")
        if cached["valid"] != row["valid"] or (cached["profile"]["window_rates"] if cached["valid"] else None) != row["rates"]:
            raise ValueError("calibration trial differs from cache")
        cases.append({"id": f"calibration-{index:02}", "program": row["program"], "expected": comparable(cached)})
    if len(cases) != 64:
        raise ValueError("full corpus required")
    root.mkdir(parents=True, exist_ok=False)
    write(root / "spec.json", read(corpus / "manifest.json")["spec"])
    prepare(ROOT, root / "spec.json", root / "run")
    write(root / "config.json", {"cases": cases, "calibration": bank["calibration"],
                                 "original_manifest_sha256": digest(corpus / "manifest.json")})
    write(root / "freeze.json", {"config": digest(root / "config.json"), "driver": digest(Path(__file__))})
    return {"cases": 64, "executed": False}


def run(root):
    if read(root / "freeze.json") != {"config": digest(root / "config.json"), "driver": digest(Path(__file__))}:
        raise ValueError("frozen replay changed")
    config = read(root / "config.json")
    m = verify_inputs(ROOT, root / "run")

    def evaluate(case):
        result, _ = measured(case["program"], root / "run", m["measurement_fingerprint"], m["runtime"]["image_id"])
        row = {"id": case["id"], "program": case["program"], "measurement": result,
               "exact_measurement_match": comparable(result) == case["expected"]}
        ensure(root / "run/panel" / case["id"] / "result.json", row)
        print({"case": case["id"], "match": row["exact_measurement_match"]}, flush=True)
        return row

    with concurrent.futures.ThreadPoolExecutor(max_workers=18) as pool:
        rows = list(pool.map(evaluate, config["cases"]))
    summary = {"charged_slots": len(rows), "results": rows,
               "exact_measurement_match": all(r["exact_measurement_match"] for r in rows),
               "new_measurement_fingerprint": m["measurement_fingerprint"],
               "old_measurement_fingerprint": config["calibration"]["measurement_fingerprint"]}
    ensure(root / "run/complete.json", summary)
    return {k: v for k, v in summary.items() if k != "results"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "run"))
    parser.add_argument("--corpus", type=Path)
    parser.add_argument("--bank", type=Path)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "plan":
        if args.corpus is None or args.bank is None:
            parser.error("corpus and bank required")
        print(plan(args.corpus, args.bank, args.directory))
    else:
        if not args.execute:
            parser.error("execute required")
        print(run(args.directory))
