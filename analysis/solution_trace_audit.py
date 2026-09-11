"""Re-bin retained FSTs without replay; independent streaming transition counter."""

import argparse
import concurrent.futures
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from analysis.solution_audit import read


def stream(lines, begin, end, core, clock_name):
    scope = []
    selected = set()
    clock = None
    values = {}
    previous_clock = None
    time = 0
    header = True
    bins = [0] * 32
    edges = [0] * 32
    checked = False
    for line in lines:
        if header:
            fields = line.split()
            if not fields:
                continue
            if fields[0] == "$scope":
                scope.append(fields[2])
            elif fields[0] == "$upscope":
                scope.pop()
            elif fields[0] == "$var":
                name = ".".join([*scope, fields[4]])
                identifier = fields[3]
                if name == clock_name:
                    clock = identifier
                if (
                    name.startswith(core + ".")
                    and ".cs_registers_i." not in name
                    and fields[1] != "parameter"
                ):
                    selected.add(identifier)
            elif fields[0] == "$enddefinitions":
                header = False
                selected.discard(clock)
                if not selected or clock is None:
                    raise ValueError("missing scope/clock")
            continue
        if line.startswith("#"):
            time = int(line[1:])
            if time >= begin and not checked:
                if any(values.get(k) is None for k in selected):
                    raise ValueError("unknown carried state")
                checked = True
            continue
        if line.startswith("b"):
            value, identifier = line[1:].split()
        elif line and line[0] in "01xXzZ":
            value, identifier = line[0], line[1:].strip()
        else:
            continue
        inside = begin <= time < end
        index = (time - begin) * 32 // (end - begin) if inside else None
        if identifier == clock:
            if inside and previous_clock == "0" and value == "1":
                edges[index] += 1
            previous_clock = value
        if identifier not in selected:
            continue
        old = values.get(identifier)
        new = int(value, 2) if all(c in "01" for c in value) else None
        if inside and new is None:
            raise ValueError("unknown activity")
        if inside and old is not None:
            bins[index] += (old ^ new).bit_count()
        values[identifier] = new
    if time < end or not checked or not all(edges):
        raise ValueError("incomplete waveform")
    return bins, edges


def grids(counts, edges):
    boundaries = {
        "8": list(range(0, 33, 4)),
        "16": list(range(0, 33, 2)),
        "shifted_6250": [0, *range(1, 32, 4), 32],
    }
    return {
        name: {
            "rates": [sum(counts[a:b]) / sum(edges[a:b]) for a, b in zip(bounds, bounds[1:])],
            "cycles": [sum(edges[a:b]) for a, b in zip(bounds, bounds[1:])],
        }
        for name, bounds in boundaries.items()
    }


def measure(identifier, archive, scratch):
    profile = read(archive / "evaluations" / identifier / "run/profile.json.gz")
    waveform = scratch / "cache" / identifier / "run/sim.fst"
    if not waveform.exists():
        return {"cache_id": identifier, "missing": True}
    checksum = hashlib.sha256()
    with waveform.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            checksum.update(chunk)
    sha = checksum.hexdigest()
    if sha != profile["waveform_sha256"]:
        raise ValueError("waveform digest mismatch")
    with subprocess.Popen(
        ["fst2vcd", str(waveform)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ) as proc:
        try:
            counts, edges = stream(
                proc.stdout,
                profile["begin_tick"],
                profile["end_tick"],
                profile["scope"],
                "TOP.ibex_simple_system.u_top.clk_i",
            )
        except BaseException:
            proc.kill()
            proc.communicate()
            raise
        err = proc.stderr.read()
        if proc.wait():
            raise ValueError(err)
    result = grids(counts, edges)
    if edges != [6250] * 32 or result["8"]["rates"] != profile["window_rates"]:
        raise ValueError("independent reconstruction differs from frozen measurement")
    return {
        "cache_id": identifier,
        "waveform_sha256": sha,
        "grids": result,
        "counts_32": counts,
        "clock_edges_32": edges,
        "begin_tick": profile["begin_tick"],
        "end_tick": profile["end_tick"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    archive = Path("results/nonflat_temporal_v1")
    scale = read(archive / "manifest.json")["scale"]
    selection = read(Path("results/solution_audit_v1/inspection.json"))
    candidates = [c for c in selection["cases"] if c["detailed"] and "best" in c["roles"]]
    targets = read(archive / "targets.json")
    ids = {c["cache_id"] for c in candidates} | {t["witness_cache_id"] for t in targets}
    args.out.mkdir(exist_ok=False)

    def one(identifier):
        result = measure(identifier, archive, Path("out/nonflat-temporal-v1"))
        with (args.out / (identifier + ".json")).open("x") as f:
            json.dump(result, f, indent=2)
            f.write("\n")
        print("Converted retained trace", identifier, flush=True)
        return identifier, result

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        measured = dict(pool.map(one, sorted(ids)))
    comparisons = []
    for c in candidates:
        witness = next(t for t in targets if t["id"] == c["target"])["witness_cache_id"]
        left, right = measured[c["cache_id"]], measured[witness]
        errors = {}
        if not left.get("missing") and not right.get("missing"):
            for name, grid in left["grids"].items():
                target = right["grids"][name]
                errors[name] = (
                    sum(
                        w * (a - b) ** 2
                        for a, b, w in zip(grid["rates"], target["rates"], grid["cycles"])
                    )
                    / sum(grid["cycles"])
                ) ** 0.5 / scale
        comparisons.append(
            {k: c[k] for k in ("target", "seed", "arm", "slot", "loss", "cache_id")}
            | {"matched_witness_errors": errors}
        )
    result = {
        "comparisons": comparisons,
        "scope": "Fixed physical window; shifted grid retains shorter end bins, cycle-weighted NRMSE. Measured witness targets, not interpolated targets. Sensitivity diagnostic, not a new solve endpoint.",
        "converter": shutil.which("fst2vcd"),
        "traces": len(measured),
        "missing": sum(r.get("missing", False) for r in measured.values()),
    }
    with (args.out / "summary.json").open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
