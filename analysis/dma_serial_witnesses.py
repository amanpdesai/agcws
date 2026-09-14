"""Declared serialized DMA initialization proposals for analytic window-v3 targets."""

import argparse
import hashlib
import runpy
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline.dma import DmaTemporal
from agcws.pipeline.metrics import error, key
from agcws.pipeline.storage import read, write
from agcws.pipeline.targets import qualify
from agcws.workloads.schedule import expand_schedule


def config(bank):
    if bank["calibration"]["domain"] != "dma-temporal" or DmaTemporal.clock_edges != 9216:
        raise ValueError("DMA window-v3 bank and runtime required")
    initial = runpy.run_path(ROOT / "analysis/schedule_refinement.py")["initial_schedules"]
    design = DmaTemporal()
    cases = []
    for split, part in bank["splits"].items():
        for request in part["requests"]:
            proposals = initial(request["rates"], bank["calibration"]["low"], design.contract, 9216)
            for index, proposal in enumerate(proposals):
                sequence = []
                for node in expand_schedule(proposal, design.contract):
                    if node["op"] == "work":
                        sequence.extend({"op": "work", "units": 1} for _ in range(node["units"]))
                    else:
                        sequence.append(node)
                program = {"sequence": sequence}
                expand_schedule(program, design.contract)
                cases.append({"id": f"{split}-{request['id']}-lead-{index}", "program": program})
    return {"name": "dma-window-v3-serialized-witnesses", "domain": "dma-temporal", "max_workers": 18,
            "scope": "CPU witness proposals, not a policy comparison; all 54 proposals are charged",
            "cases": cases}


def analyze(root, bank_path):
    bank = read(bank_path)
    manifest = read(root / "manifest.json")
    if read(root / "freeze.json")["manifest_sha256"] != hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest():
        raise ValueError("manifest changed")
    if (manifest["config"] != config(bank)
            or manifest["measurement"]["measurement_fingerprint"] != bank["calibration"]["measurement_fingerprint"]):
        raise ValueError("frozen proposals or measurement differ")
    terminal = read(root / "complete.json")
    if terminal["charged_slots"] != 54 or len(terminal["results"]) != 54:
        raise ValueError("complete 54-proposal panel required")
    design = DmaTemporal()
    by_id = {}
    for case, row in zip(manifest["config"]["cases"], terminal["results"], strict=True):
        if row["id"] != case["id"] or row["program"] != case["program"]:
            raise ValueError("case identity differs")
        if read(root / "panel" / case["id"] / "result.json") != row:
            raise ValueError("case checkpoint differs")
        result = row["measurement"]
        canonical = design.canonical(case["program"])
        identifier = key({"program": canonical, "measurement": manifest["measurement"]["measurement_fingerprint"]})
        if result["cache_id"] != identifier or read(root / "cache" / identifier / "result.json") != result:
            raise ValueError("cache evidence differs")
        if not result["valid"]:
            if result.get("rates") is not None:
                raise ValueError("invalid proposal has rates")
        else:
            paths = list((root / "cache" / identifier).glob("attempt-*/activity.json"))
            if len(paths) != 1:
                raise ValueError("missing or ambiguous activity")
            attempt = paths[0].parent
            if read(attempt / "program.json") != canonical or not design.completed(attempt)["valid"]:
                raise ValueError("executed program or functional completion differs")
            activity = read(paths[0])
            samples = activity["per_cycle_toggles"]
            if len(samples) != 9216 or activity["clock_edges"] != 9216:
                raise ValueError("observation window differs")
            rates = [sum(samples[i*1152:(i+1)*1152])/1152 for i in range(8)]
            if (rates != result["rates"] or rates != result["profile"]["window_rates"]
                    or result["profile"]["scope"] != "axi_dma" or result["profile"]["fidelity"] != "activity"):
                raise ValueError("DUT profile does not reconstruct")
        by_id[case["id"]] = result
    reports = []
    for split, part in bank["splits"].items():
        for request in part["requests"]:
            identifiers = [f"{split}-{request['id']}-lead-{i}" for i in range(3)]
            valid = [name for name in identifiers if by_id[name]["valid"]]
            best = min(valid, key=lambda name: (error(by_id[name]["rates"], request["rates"], bank["calibration"]["scale"]), name)) if valid else None
            result = by_id[best] if best else {"valid": False}
            reports.append({"id": f"{split}-{request['id']}", "control": request["control"],
                            "witness_case": best, "witness": result, "charged_slots": 3,
                            "invalid_cases": [name for name in identifiers if not by_id[name]["valid"]],
                            **qualify(request, result, scale=bank["calibration"]["scale"], tolerance=.1, nonflat_margin=.02)})
    return {"scope": "measured qualification, no policy inference or independent waveform resimulation",
            "bank_sha256": hashlib.sha256(bank_path.read_bytes()).hexdigest(), "reports": reports,
            "qualified": sum(r["qualified"] for r in reports), "charged_slots": 54}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "audit"))
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "audit" and args.directory is None:
        parser.error("audit requires --directory")
    write(args.output, config(read(args.bank)) if args.action == "prepare" else analyze(args.directory, args.bank))
