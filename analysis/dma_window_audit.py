"""Check completion and padded-tail activity in existing DMA qualification data."""

import argparse
import hashlib
from collections import Counter
from pathlib import Path
from statistics import median

from agcws.pipeline.metrics import key
from agcws.pipeline.storage import read, write
from agcws.workloads.schedule import ScheduleContract, expand_schedule


def timing(observed):
    required = {"read_descriptors": 64, "write_completions": 64,
                "useful_work_bytes": 4096, "observation_cycles": 12000,
                "padded_until_ns": 120005}
    if any(observed.get(k) != v for k, v in required.items()):
        raise ValueError("DMA functional/window record differs from v2 contract")
    completion = observed["completion_ns"]
    end = observed["declared_schedule_end_ns"]
    if not 0 <= completion <= end <= 120000:
        raise ValueError("completion/schedule end outside observation window")
    trailing = observed["trailing_idle_cycles"]
    if type(trailing) is not int or trailing < 0 or abs(end-completion-trailing*10) > 20:
        raise ValueError("trailing wait does not reconstruct schedule end")
    return {"completion_cycles": completion/10,
            "schedule_end_cycles": end/10,
            "padding_cycles": (120000-end)/10}


def analyze(root):
    digest = hashlib.sha256()

    def record(path):
        digest.update(str(path.relative_to(root)).encode()+b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
        return read(path)

    manifest = record(root / "manifest.json")
    if manifest["spec"]["domain"] != "dma-temporal":
        raise ValueError("DMA panel required")
    terminal = record(root / "complete.json")
    programs, invalid, slots = {}, Counter(), 0
    for path in sorted((root / "panel").glob("*/*/*/batches/*/trials.json")):
        for trial in record(path):
            slots += 1
            if trial["valid"] is not True:
                if trial.get("loss") is not None:
                    raise ValueError("invalid trial was scored")
                invalid[trial["stage"]] += 1
                continue
            canonical = {"sequence": expand_schedule(trial["program"], ScheduleContract(64, 6000))}
            identifier = key({"program": canonical, "measurement": manifest["measurement_fingerprint"]})
            if identifier != trial["cache_id"]:
                raise ValueError("trial cache identity differs")
            value = (canonical, trial["rates"])
            if identifier in programs and programs[identifier] != value:
                raise ValueError("one cache identity has conflicting evidence")
            programs[identifier] = value
    if slots != terminal["slots"] or not programs:
        raise ValueError("missing terminal slots or valid evidence")
    rows = []
    for identifier, (program, rates) in sorted(programs.items()):
        cache = root / "cache" / identifier
        result = record(cache / "result.json")
        if result["valid"] is not True or result["rates"] != rates:
            raise ValueError("trial and cached result differ")
        matches = list(cache.glob("attempt-*/sim_build/observed.json"))
        if len(matches) != 1:
            raise ValueError("missing or ambiguous functional record")
        observed = record(matches[0])
        attempt = matches[0].parents[1]
        if record(attempt / "program.json") != program:
            raise ValueError("executed program differs")
        activity = record(attempt / "activity.json")
        samples = activity["per_cycle_toggles"]
        if activity["clock_edges"] != 12000 or len(samples) != 12000:
            raise ValueError("activity window differs")
        reconstructed = [sum(samples[i*1500:(i+1)*1500])/1500 for i in range(8)]
        if (reconstructed != rates or result["profile"]["scope"] != "axi_dma"
                or result["profile"]["fidelity"] != "activity"):
            raise ValueError("DUT activity rates do not reconstruct")
        rows.append({"cache_id": identifier, **timing(observed), "rates": rates})
    fields = ("completion_cycles", "schedule_end_cycles", "padding_cycles")
    return {"scope": "measured DMA corpus timing; not proof of all legal workloads' reachability",
            "manifest_sha256": hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest(),
            "input_evidence_sha256": digest.hexdigest(), "slots": slots,
            "invalid_by_stage": dict(invalid), "unique_valid": len(rows),
            "timing": {field: {"min": min(r[field] for r in rows),
                               "median": median(r[field] for r in rows),
                               "max": max(r[field] for r in rows)} for field in fields},
            "bin_ranges": [{"min": min(r["rates"][i] for r in rows),
                            "max": max(r["rates"][i] for r in rows)} for i in range(8)],
            "rows": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write(args.output, analyze(args.directory))
