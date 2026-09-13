"""Fixed CPU diagnostic, reusing the shared backend without a search policy."""

import argparse
import concurrent.futures
import fcntl
import hashlib
import json
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import verify_inputs
from agcws.pipeline.redmule import RedmuleTemporal
from agcws.pipeline.storage import ensure, read, write


def programs():
    cases = []
    for size in (4, 8, 16):
        minimum = max(1, (1024+size**3-1)//size**3)
        for pattern in ("zeros", "alternating", "random"):
            for multiplier in (1, 2, 4):
                for pacing, duration in (("queued", 1), ("paced", 49152)):
                    cases.append({"id": f"size{size}-{pattern}-x{multiplier}-{pacing}",
                                  "program": {"size": size, "pattern": pattern, "data_seed": 7500,
                                              "phases": [{"start": 2048, "duration": duration,
                                                          "jobs": minimum*multiplier}]}})
    return cases


def prepare(reference, root):
    measurement = verify_inputs(ROOT, reference)
    if measurement["spec"]["domain"] != "redmule-temporal":
        raise ValueError("RedMulE measurement reference required")
    manifest = {"kind": "fixed-pacing-diagnostic-v1", "measurement": measurement,
                "driver_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "cases": programs(), "max_workers": 12,
                "scope": "CPU diagnostic, not search, target qualification or policy inference"}
    root.mkdir(parents=True, exist_ok=False)
    write(root / "manifest.json", manifest)
    return {"prepared_cases": len(manifest["cases"])}


def run(reference, root):
    manifest = read(root / "manifest.json")
    if (manifest["measurement"] != verify_inputs(ROOT, reference)
            or manifest["cases"] != programs()
            or manifest["driver_sha256"] != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            or manifest["max_workers"] != 12):
        raise ValueError("frozen diagnostic inputs changed")
    with (root / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

        def measure(case):
            path = root / "panel" / case["id"] / "result.json"
            if path.exists():
                record = read(path)
                if record["id"] != case["id"] or record["program"] != case["program"]:
                    raise ValueError("checkpoint differs from frozen probe")
                cached = root / "cache" / record["measurement"]["cache_id"] / "result.json"
                if read(cached) != record["measurement"]:
                    raise ValueError("probe checkpoint differs from cached measurement")
                return record
            result, _ = RedmuleTemporal().measured(case["program"], root, manifest["measurement"])
            record = {"id": case["id"], "program": case["program"], "measurement": result}
            write(path, record)
            print(json.dumps({"case": case["id"], "valid": result["valid"],
                              "stage": result.get("stage")}), flush=True)
            return record

        with concurrent.futures.ThreadPoolExecutor(max_workers=manifest["max_workers"]) as pool:
            results = list(pool.map(measure, manifest["cases"]))
        summary = {"kind": manifest["kind"], "cases": len(results),
                   "valid": sum(r["measurement"]["valid"] for r in results),
                   "results": results}
        ensure(root / "complete.json", summary)
        return {key: summary[key] for key in ("kind", "cases", "valid")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run"))
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "run" and not args.execute:
        parser.error("run requires --execute")
    function = prepare if args.action == "prepare" else run
    print(json.dumps(function(args.reference.resolve(), args.directory.resolve())))


if __name__ == "__main__":
    main()
