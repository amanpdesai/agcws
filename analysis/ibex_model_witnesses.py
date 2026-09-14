"""Measured rectangular-mixture model proposes witnesses; simulation decides validity."""

import argparse
import concurrent.futures
import hashlib
import statistics
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.engine import prepare, verify_inputs
from agcws.pipeline.ibex.cache import measured
from agcws.pipeline.ibex.program import allocate, canonical
from agcws.pipeline.metrics import error
from agcws.pipeline.storage import ensure, read, write
from agcws.pipeline.targets import qualify


def model(rows, preset):
    selected = [r for r in rows if r["id"].startswith(f"preset-{preset}-")]
    if len(selected) != 8 or not all(r["measurement"]["valid"] for r in selected):
        raise ValueError("eight valid measured mixture probes required")
    idle = statistics.median(r["measurement"]["profile"]["window_rates"][-1] for r in selected)
    options = []
    for r in selected:
        result = r["measurement"]
        body = result["execution"]["phases"]["segment_0_body"]
        cycles = (body["last_retired_cycle"] - body["first_retired_cycle"] + 1)/4096
        deficit = (idle*200000 - sum(result["profile"]["window_bit_transitions"]))/4096
        if deficit <= 0:
            raise ValueError("nonpositive measured activity deficit")
        options.append({"cycles": cycles, "deficit": deficit, "body": r["program"]["segments"][0]["body"],
                        "registers": r["program"]["registers"]})
    return idle, options


def propose(rates, rows):
    candidates = []
    for preset in range(3):
        idle, options = model(rows, preset)
        deficits = [max(0, idle-rate)*25000 for rate in rates]
        total = sum(deficits)
        if total <= 0:
            raise ValueError("target has no modeled activity deficit")
        beam = [([], [])]
        for index, deficit in enumerate(deficits):
            expanded = []
            for choices, counts in beam:
                for choice, option in enumerate(options):
                    count = max(1, min(4096, round(deficit/option["deficit"])))
                    expanded.append((choices+[choice], counts+[count]))
            desired = 4096*sum(deficits[:index+1])/total
            beam = sorted(expanded, key=lambda pair: (abs(sum(pair[1])-desired), pair[0]))[:128]
        ranked = []
        for choices, counts in beam:
            allocated = allocate(counts)
            predictions = [idle-options[c]["deficit"]*n/25000 for c,n in zip(choices, allocated)]
            overflow = sum(max(0, options[c]["cycles"]*n-24900)/25000 for c,n in zip(choices, allocated))
            ranked.append((error(predictions, rates, 1)+1000*overflow, choices, counts, allocated))
        for rank, (_, choices, weights, allocated) in enumerate(sorted(ranked)[:2]):
            for lead in (0.0, 0.5):
                segments = []
                for index, (choice, weight, count) in enumerate(zip(choices, weights, allocated)):
                    option = options[choice]
                    release = index*25000+round(lead*max(0, 24900-count*option["cycles"]))
                    segments.append({"weight": weight, "release": release, "body": option["body"]})
                candidates.append({"variant": f"preset-{preset}-rank-{rank}-lead-{lead}",
                    "program": canonical({"registers": options[0]["registers"], "memory_seed": 0, "segments": segments})})
    return candidates


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan(probe, bank_path, root):
    m = verify_inputs(ROOT, probe / "run")
    rows = read(probe / "run/complete.json")["results"]
    bank = read(bank_path)
    cases = []
    for split, part in bank["splits"].items():
        for request in part["requests"]:
            for proposal in propose(request["rates"], rows):
                cases.append({"id": f"{split}-{request['id']}-{proposal['variant']}",
                              "request_id": f"{split}-{request['id']}", "program": proposal["program"]})
    root.mkdir(parents=True, exist_ok=False)
    write(root / "spec.json", m["spec"])
    prepare(ROOT, root / "spec.json", root / "run")
    write(root / "config.json", {"bank": bank, "cases": cases, "probe_rows": rows,
                                 "probe_manifest_sha256": digest(probe / "run/manifest.json")})
    write(root / "freeze.json", {"config": digest(root / "config.json"), "driver": digest(Path(__file__))})
    return {"cases": len(cases), "executed": False}


def run(root):
    if read(root / "freeze.json") != {"config": digest(root / "config.json"), "driver": digest(Path(__file__))}:
        raise ValueError("frozen proposals changed")
    config = read(root / "config.json")
    m = verify_inputs(ROOT, root / "run")

    def evaluate(case):
        result, _ = measured(case["program"], root / "run", m["measurement_fingerprint"], m["runtime"]["image_id"])
        row = {**case, "measurement": result}
        ensure(root / "run/panel" / case["id"] / "result.json", row)
        print({"case": case["id"], "valid": result["valid"]}, flush=True)
        return row

    with concurrent.futures.ThreadPoolExecutor(max_workers=18) as pool:
        rows = list(pool.map(evaluate, config["cases"]))
    scale = config["bank"]["calibration"]["scale"]
    reports = []
    for split, part in config["bank"]["splits"].items():
        for request in part["requests"]:
            name = f"{split}-{request['id']}"
            valid = [r for r in rows if r["request_id"] == name and r["measurement"]["valid"]]
            best = min(valid, key=lambda r: (error(r["measurement"]["profile"]["window_rates"], request["rates"], scale), r["id"])) if valid else None
            witness = {"valid": False} if best is None else {**best["measurement"], "rates": best["measurement"]["profile"]["window_rates"]}
            reports.append({"id": name, "witness_case": best["id"] if best else None,
                            **qualify(request, witness, scale=scale, tolerance=.1, nonflat_margin=.02)})
    ensure(root / "run/complete.json", {"charged_slots": len(rows), "results": rows, "reports": reports})
    return {"charged_slots": len(rows), "qualified": sum(r["qualified"] for r in reports)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "run"))
    parser.add_argument("--probe", type=Path)
    parser.add_argument("--bank", type=Path)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "plan":
        if args.probe is None or args.bank is None:
            parser.error("probe and bank required")
        print(plan(args.probe, args.bank, args.directory))
    else:
        if not args.execute:
            parser.error("execute required")
        print(run(args.directory))
