"""Frozen division/ALU mixtures through the existing Ibex evaluator."""

import argparse
import concurrent.futures
import fcntl
import hashlib
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.ibex.cache import measured
from agcws.pipeline.ibex.program import canonical
from agcws.pipeline.storage import ensure, read, write


def cases():
    rows = []
    for preset, registers in enumerate(([1]*8, [0xffffffff, 3, 7, 11, 13, 17, 19, 23],
                                       [0xaaaaaaaa, 0x55555555, 3, 7, 11, 13, 17, 19])):
        for divisions in range(1, 9):
            body = [{"op": "divu" if i < divisions else "xor", "a": 0, "b": 1, "dst": 7} for i in range(8)]
            rows.append({"id": f"preset-{preset}-divisions-{divisions}", "program": canonical({
                "registers": registers, "memory_seed": 0,
                "segments": [{"weight": 1, "release": 0, "body": body}]})})
    return rows


def plan(reference, root):
    old = verify_inputs(ROOT, reference)
    if old["spec"]["domain"] != "ibex-temporal":
        raise ValueError("Ibex reference required")
    root.mkdir(parents=True, exist_ok=False)
    write(root / "spec.json", old["spec"])
    prepare(ROOT, root / "spec.json", root / "run")
    write(root / "config.json", {"cases": cases(), "max_workers": 18})
    write(root / "freeze.json", {"config": digest(root / "config.json"), "driver": digest(Path(__file__))})
    return {"cases": 24, "executed": False}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(root):
    if read(root / "freeze.json") != {"config": digest(root / "config.json"), "driver": digest(Path(__file__))}:
        raise ValueError("frozen inputs changed")
    config = read(root / "config.json")
    if config["cases"] != cases():
        raise ValueError("program regeneration differs")
    manifest = verify_inputs(ROOT, root / "run")

    def evaluate(case):
        result, _ = measured(case["program"], root / "run", manifest["measurement_fingerprint"], manifest["runtime"]["image_id"])
        row = {**case, "measurement": result}
        ensure(root / "run/panel" / case["id"] / "result.json", row)
        print({"case": case["id"], "valid": result["valid"]}, flush=True)
        return row

    with (root / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with concurrent.futures.ThreadPoolExecutor(max_workers=18) as pool:
            rows = list(pool.map(evaluate, config["cases"]))
        ensure(root / "run/complete.json", {"charged_slots": 24, "results": rows})
    return {"charged_slots": 24, "valid": sum(r["measurement"]["valid"] for r in rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "run"))
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "plan":
        if args.reference is None:
            parser.error("reference required")
        print(plan(args.reference, args.directory))
    else:
        if not args.execute:
            parser.error("execute required")
        print(run(args.directory))
