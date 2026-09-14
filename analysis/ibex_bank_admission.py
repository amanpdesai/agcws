"""Replay selected Ibex witnesses; admit only with a complete calibration bridge."""

import argparse
import concurrent.futures
import hashlib
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.ibex.cache import measured
from agcws.pipeline.ibex.program import canonical, interpret
from agcws.pipeline.metrics import error, key
from agcws.pipeline.storage import ensure, read, write
from agcws.pipeline.targets import qualify


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select(config, complete):
    if complete["charged_slots"] != 216 or len(complete["results"]) != 216:
        raise ValueError("complete original witness search required")
    scale = config["bank"]["calibration"]["scale"]
    cases = []
    for split, part in config["bank"]["splits"].items():
        for request in part["requests"]:
            name = f"{split}-{request['id']}"
            candidates = [r for r in complete["results"] if r["request_id"] == name and r["measurement"]["valid"]]
            if not candidates:
                raise ValueError("request has no valid witness")
            best = min(candidates, key=lambda r: (error(r["measurement"]["profile"]["window_rates"], request["rates"], scale), r["id"]))
            witness = {**best["measurement"], "rates": best["measurement"]["profile"]["window_rates"]}
            checked = {"id": name, "witness_case": best["id"],
                       **qualify(request, witness, scale=scale, tolerance=.1, nonflat_margin=.02)}
            if checked not in complete["reports"] or not checked["qualified"]:
                raise ValueError("original qualification differs or fails")
            cases.append({"id": name, "split": split, "request": request,
                          "program": best["program"], "expected": best["measurement"]})
    if len(cases) != 18:
        raise ValueError("eighteen requests required")
    return cases


def plan(source, root):
    config, complete = read(source / "config.json"), read(source / "run/complete.json")
    cases = select(config, complete)
    root.mkdir(parents=True, exist_ok=False)
    write(root / "spec.json", read(source / "run/manifest.json")["spec"])
    prepare(ROOT, root / "spec.json", root / "run")
    write(root / "config.json", {"bank": config["bank"], "cases": cases,
                                 "original_complete_sha256": digest(source / "run/complete.json"),
                                 "original_manifest_sha256": digest(source / "run/manifest.json")})
    write(root / "freeze.json", {"config": digest(root / "config.json"), "driver": digest(Path(__file__))})


def inputs(root):
    if read(root / "freeze.json") != {"config": digest(root / "config.json"), "driver": digest(Path(__file__))}:
        raise ValueError("frozen admission inputs changed")
    return read(root / "config.json"), verify_inputs(ROOT, root / "run")


def semantic(result):
    return {"valid": result["valid"], "stage": result["stage"],
            "profile": {k: v for k, v in result["profile"].items() if k not in ("extraction_s", "waveform_sha256")},
            **{k: result[k] for k in ("allocation", "feedback", "execution")}}


def run(root):
    config, manifest = inputs(root)

    def replay(case):
        result, _ = measured(case["program"], root / "run", manifest["measurement_fingerprint"], manifest["runtime"]["image_id"])
        row = {"id": case["id"], "program": case["program"], "measurement": result}
        ensure(root / "run/panel" / case["id"] / "result.json", row)
        print({"case": case["id"], "valid": result["valid"]}, flush=True)
        return row

    with concurrent.futures.ThreadPoolExecutor(max_workers=18) as pool:
        rows = list(pool.map(replay, config["cases"]))
    ensure(root / "run/complete.json", {"charged_slots": 18, "results": rows})


def admit(root, calibration):
    config, manifest = inputs(root)
    bridge = verify_inputs(ROOT, calibration / "run")
    if bridge["measurement_fingerprint"] != manifest["measurement_fingerprint"]:
        raise ValueError("calibration and witnesses use different runtimes")
    if read(calibration / "config.json")["calibration"] != config["bank"]["calibration"]:
        raise ValueError("calibration lineage differs")
    wave = read(calibration / "run/waveform-audit.json")
    bindings = wave.get("bindings", {})
    for name, path in (("driver", ROOT / "analysis/ibex_waveform_replay.py"),
                       ("replay_config", calibration / "config.json"),
                       ("replay_complete", calibration / "run/complete.json"),
                       ("replay_manifest", calibration / "run/manifest.json")):
        if bindings.get(name) != digest(path):
            raise ValueError("calibration waveform receipt has stale or missing input bindings")
    if bindings.get("original_manifest") != read(calibration / "config.json")["original_manifest_sha256"]:
        raise ValueError("original calibration manifest differs")
    if (wave["cases"] != 64 or wave["matched"] != 64 or len(wave["records"]) != 64
            or not all(r["match"] for r in wave["records"])):
        raise ValueError("complete calibration waveform bridge required")
    complete = read(root / "run/complete.json")
    if complete["charged_slots"] != 18 or len(complete["results"]) != 18:
        raise ValueError("all witnesses required")
    bank = config["bank"]
    result = {"domain": "ibex-temporal", "target_bank_qualified": True, "full_study_ready": False,
              "calibration": {**bank["calibration"], "measurement_fingerprint": manifest["measurement_fingerprint"]},
              "qualification_procedures": [bank["procedure"], "docs/IBEX_MODEL_WITNESSES_V1.md", "docs/IBEX_BANK_ADMISSION_V1.md"],
              "splits": {name: {"requests": [], "pairwise_distances": part["pairwise_distances"]} for name, part in bank["splits"].items()},
              "lineage": {"original_complete_sha256": config["original_complete_sha256"],
                          "calibration_waveform_audit_sha256": digest(calibration / "run/waveform-audit.json"),
                          "replay_manifest_sha256": digest(root / "run/manifest.json")}}
    for case, row in zip(config["cases"], complete["results"], strict=True):
        measurement = row["measurement"]
        if row["id"] != case["id"] or row["program"] != case["program"]:
            raise ValueError("case pairing differs")
        identifier = key({"program": canonical(case["program"]), "measurement": manifest["measurement_fingerprint"]})
        if measurement["cache_id"] != identifier or read(root / "run/cache" / identifier / "result.json") != measurement:
            raise ValueError("cache identity differs")
        if not measurement["valid"] or semantic(measurement) != semantic(case["expected"]):
            raise ValueError("witness no longer reproduces its measured profile or execution")
        functional = read(root / "run/cache" / identifier / "run/functional.json")
        if functional["expected"] != interpret(case["program"]) or functional["functional_ok"] is not True:
            raise ValueError("architectural reference differs")
        witness = {**measurement, "rates": measurement["profile"]["window_rates"]}
        checked = qualify(case["request"], witness, scale=result["calibration"]["scale"], tolerance=.1, nonflat_margin=.02)
        if not checked["qualified"]:
            raise ValueError("qualification failed on replay")
        result["splits"][case["split"]]["requests"].append({**case["request"], **checked,
              "witness_cache_id": identifier, "witness_case": case["id"]})
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "run", "admit"))
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--calibration", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.action == "plan":
        if args.source is None:
            parser.error("source required")
        plan(args.source, args.directory)
    elif args.action == "run":
        run(args.directory)
    else:
        if args.calibration is None or args.output is None:
            parser.error("calibration bridge and output required")
        write(args.output, admit(args.directory, args.calibration))
