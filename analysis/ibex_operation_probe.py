"""Fixed native Ibex operation probes through the existing measured cache."""

import argparse
import concurrent.futures
import hashlib
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.ibex.cache import measured
from agcws.pipeline.ibex.program import BINARY, canonical
from agcws.pipeline.storage import ensure, read, write


def cases():
    rows = []
    registers = ([0]*8, [1]*8, [0xffffffff, 3, 7, 11, 13, 17, 19, 23],
                 [0xaaaaaaaa, 0x55555555, 3, 7, 11, 13, 17, 19])
    for op in (*BINARY, "load", "store"):
        for preset, values in enumerate(registers):
            for length in (1, 8):
                inst = {"op": op, "a": 0}
                if op != "load":
                    inst["b"] = 1
                if op != "store":
                    inst["dst"] = 7
                program = canonical({"registers": list(values), "memory_seed": 0,
                    "segments": [{"weight": 1, "release": 0, "body": [inst]*length}]})
                rows.append({"id": f"{op}-{preset}-{length}", "program": program})
    return rows


def plan(reference, root):
    old = read(reference / "manifest.json")
    if old["spec"]["domain"] != "ibex-temporal":
        raise ValueError("Ibex reference required")
    root.mkdir(parents=True, exist_ok=False)
    write(root / "reference-spec.json", old["spec"])
    prepare(ROOT, root / "reference-spec.json", root / "run")
    write(root / "config.json", {"cases": cases(), "max_workers": 18,
          "scope": "operation characterization; no target admission or policy inference"})
    write(root / "freeze.json", {"config": hashlib.sha256((root / "config.json").read_bytes()).hexdigest(),
          "driver": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    return {"cases": 88, "executed": False}


def run(root):
    frozen = read(root / "freeze.json")
    if frozen != {"config": hashlib.sha256((root / "config.json").read_bytes()).hexdigest(),
                  "driver": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}:
        raise ValueError("probe changed after freeze")
    manifest = verify_inputs(ROOT, root / "run")
    config = read(root / "config.json")
    if config["cases"] != cases():
        raise ValueError("case regeneration differs")

    def evaluate(case):
        result, _ = measured(case["program"], root / "run", manifest["measurement_fingerprint"], manifest["runtime"]["image_id"])
        row = {**case, "measurement": result}
        ensure(root / "run/panel" / case["id"] / "result.json", row)
        print({"case": case["id"], "valid": result["valid"]}, flush=True)
        return row

    with concurrent.futures.ThreadPoolExecutor(max_workers=config["max_workers"]) as pool:
        rows = list(pool.map(evaluate, config["cases"]))
    ensure(root / "run/complete.json", {"charged_slots": len(rows), "results": rows})
    return {"charged_slots": len(rows), "valid": sum(r["measurement"]["valid"] for r in rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "run"))
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "plan":
        if args.reference is None:
            parser.error("reference required")
        print(plan(args.reference, args.directory))
    else:
        if not args.execute:
            parser.error("explicit execute required")
        print(run(args.directory))
