"""Frozen CPU diagnostic cases through shared measurement backends, with resume."""

import argparse
import concurrent.futures
import fcntl
import hashlib
import json
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.backends import backend
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.storage import ensure, read, write


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(config):
    if set(config) != {"name", "domain", "scope", "cases", "max_workers"}:
        raise ValueError("exact diagnostic configuration fields required")
    if type(config["max_workers"]) is not int or config["max_workers"] < 1:
        raise ValueError("positive integer worker count required")
    if not config["cases"]:
        raise ValueError("fixed cases required")
    names = []
    for case in config["cases"]:
        if set(case) != {"id", "program"} or not isinstance(case["program"], dict):
            raise ValueError("case requires id and native program")
        name = case["id"]
        if not isinstance(name, str) or not name or Path(name).name != name or name in (".", ".."):
            raise ValueError("safe single-component case id required")
        names.append(name)
    if len(set(names)) != len(names):
        raise ValueError("unique case identifiers required")
    if not hasattr(backend(config["domain"]), "measured"):
        raise ValueError("backend does not expose native diagnostic measurement")
    return config


def prepare(reference, config_path, root):
    config = validate(read(config_path))
    measurement = verify_inputs(ROOT, reference)
    if measurement["spec"]["domain"] != config["domain"]:
        raise ValueError("measurement domain differs from cases")
    root.mkdir(parents=True, exist_ok=False)
    write(root / "manifest.json", {"kind": "fixed-native-diagnostic-v1", "config": config,
                                   "measurement": measurement, "config_sha256": sha(config_path),
                                   "driver_sha256": sha(Path(__file__))})
    write(root / "freeze.json", {"manifest_sha256": sha(root / "manifest.json")})
    return {"cases": len(config["cases"]), "executed": False}


def run(reference, root):
    if read(root / "freeze.json") != {"manifest_sha256": sha(root / "manifest.json")}:
        raise ValueError("manifest changed")
    manifest = read(root / "manifest.json")
    config = validate(manifest["config"])
    if manifest["driver_sha256"] != sha(Path(__file__)) or manifest["measurement"] != verify_inputs(ROOT, reference):
        raise ValueError("frozen driver or measurement changed")
    design = backend(config["domain"])

    def measure(case):
        result, _ = design.measured(case["program"], root, manifest["measurement"])
        record = {**case, "measurement": result}
        ensure(root / "panel" / case["id"] / "result.json", record)
        print(json.dumps({"case": case["id"], "valid": result["valid"], "stage": result.get("stage")}), flush=True)
        return record

    with (root / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with concurrent.futures.ThreadPoolExecutor(max_workers=config["max_workers"]) as pool:
            rows = list(pool.map(measure, config["cases"]))
        summary = {"kind": manifest["kind"], "charged_slots": len(rows),
                   "valid": sum(row["measurement"]["valid"] for row in rows), "results": rows}
        ensure(root / "complete.json", summary)
    return {k: summary[k] for k in ("charged_slots", "valid")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run"))
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "prepare":
        if args.config is None:
            parser.error("prepare requires --config")
        result = prepare(args.reference.resolve(), args.config.resolve(), args.directory.resolve())
    else:
        if not args.execute:
            parser.error("run requires --execute")
        result = run(args.reference.resolve(), args.directory.resolve())
    print(json.dumps(result))
