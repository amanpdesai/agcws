"""Reconstruct frozen mixture proposals, architectural checks and target admission."""

import argparse
import hashlib
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.ibex.program import canonical, interpret
from agcws.pipeline.metrics import error, key
from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import qualify


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(root):
    if read(root / "freeze.json") != {"config": digest(root / "config.json"),
                                     "driver": digest(ROOT / "analysis/ibex_model_witnesses.py")}:
        raise ValueError("frozen model or input differs")
    config = read(root / "config.json")
    manifest = verify_inputs(ROOT, root / "run")
    bank = config["bank"]
    propose = runpy.run_path(ROOT / "analysis/ibex_model_witnesses.py")["propose"]
    cases = []
    for split, part in bank["splits"].items():
        for request in part["requests"]:
            for p in propose(request["rates"], config["probe_rows"]):
                cases.append({"id": f"{split}-{request['id']}-{p['variant']}",
                              "request_id": f"{split}-{request['id']}", "program": p["program"]})
    if config["cases"] != cases or len(cases) != 216:
        raise ValueError("proposal regeneration differs")
    complete = read(root / "run/complete.json")
    if complete["charged_slots"] != 216 or len(complete["results"]) != 216:
        raise ValueError("complete panel required")
    for case, row in zip(cases, complete["results"], strict=True):
        if {k: row[k] for k in case} != case:
            raise ValueError("case identity differs")
        if read(root / "run/panel" / case["id"] / "result.json") != row:
            raise ValueError("checkpoint differs")
        result = row["measurement"]
        identifier = key({"program": canonical(case["program"]), "measurement": manifest["measurement_fingerprint"]})
        if result["cache_id"] != identifier or read(root / "run/cache" / identifier / "result.json") != result:
            raise ValueError("cache differs")
        if not result["valid"]:
            if result.get("profile") is not None:
                raise ValueError("invalid proposal scored")
            continue
        directory = root / "run/cache" / identifier / "run"
        functional = read(directory / "functional.json")
        profile = read(directory / "profile.json")
        if (read(directory / "program.json") != canonical(case["program"])
                or functional["expected"] != interpret(case["program"])
                or functional["functional_ok"] is not True
                or functional["expected"]["useful_work"] != 4096):
            raise ValueError("functional reference differs")
        if profile != result["profile"] or profile["clock_edges"] != 200000:
            raise ValueError("measurement profile differs")
        if [n/25000 for n in profile["window_bit_transitions"]] != profile["window_rates"]:
            raise ValueError("bin arithmetic differs")
        if profile["end_tick"]-profile["begin_tick"] != 400000:
            raise ValueError("observation interval differs")
        if read(directory / "feedback.json") != result["feedback"] or read(directory / "execution.json") != result["execution"]:
            raise ValueError("execution evidence differs")
    reports = []
    for split, part in bank["splits"].items():
        for request in part["requests"]:
            name = f"{split}-{request['id']}"
            valid = [r for r in complete["results"] if r["request_id"] == name and r["measurement"]["valid"]]
            best = min(valid, key=lambda r: (error(r["measurement"]["profile"]["window_rates"], request["rates"], bank["calibration"]["scale"]), r["id"])) if valid else None
            result = {"valid": False} if best is None else {**best["measurement"], "rates": best["measurement"]["profile"]["window_rates"]}
            reports.append({"id": name, "witness_case": best["id"] if best else None,
                            **qualify(request, result, scale=bank["calibration"]["scale"], tolerance=.1, nonflat_margin=.02)})
    if reports != complete["reports"]:
        raise ValueError("qualification report differs")
    return {"scope": "compact evidence and reference recomputation; no independent waveform resimulation",
            "charged_slots": 216, "qualified": sum(r["qualified"] for r in reports), "reports": reports,
            "full_study_ready": False, "measurement_fingerprint": manifest["measurement_fingerprint"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, analyze(args.directory))
