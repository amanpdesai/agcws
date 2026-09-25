"""Fixed-finalist Mesh sink sensitivity. No search, model calls, or reselection."""

import argparse
import concurrent.futures
import copy
import gzip
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from statistics import mean

from agcws.core import config
from agcws.designs.aes.gls import sha
from agcws.evaluation.power.frozen import verify_sources
from agcws.reporting.metrics import error, key, max_bin_error
from agcws.reporting.power_reference import compare_measurements

ROOT = config.ROOT
OUT = ROOT / "out/mesh-sink-sensitivity-replay"
ARCHIVE = ROOT / "results/mesh/power/measurements.jsonl.gz"
SYNTHESIS = ROOT / "out/reference-repair-v1/power-preparation-v2/mesh/synthesis"
ARMS = ("flash-lite-medium", "strong-medium-64k")
RUNTIMES = {
    ARMS[0]: ROOT / "out/release-runtimes/power-flash-v1",
    ARMS[1]: ROOT / "out/release-runtimes/power-f4f4c1b3cf",
}


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".pending")
    tmp.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)


def restrict(program):
    result = copy.deepcopy(program)
    result["sink_period"] = 8
    result["sink_pause"] = min(max(program["sink_pause"], 0), 3)
    return result


def inventory():
    cases, references = [], {}
    for line in gzip.decompress(ARCHIVE.read_bytes()).splitlines():
        bucket = json.loads(line)
        for row in bucket["records"]:
            if row["status"] != "measured":
                raise ValueError("Mesh source contains an unmeasured case")
            raw = row["raw_measurement"].encode()
            import hashlib

            if hashlib.sha256(raw).hexdigest() != row["receipt"]["measurement_sha256"]:
                raise ValueError("original measurement checksum mismatch")
            measured = json.loads(raw)
            if (
                measured["activity"] != row["case"]
                or measured["plan_sha256"] != bucket["plan_sha256"]
            ):
                raise ValueError("original selection identity differs")
            c = row["case"]
            if c.get("role") == "power_reference":
                references[c["target"]] = measured
            if c["policy"] not in ARMS:
                continue
            manifest_path = Path(c["root"]) / "manifest.json"
            if sha(manifest_path) != c["manifest_sha256"]:
                raise ValueError("original manifest changed")
            manifest = read(manifest_path)
            assert manifest["spec"]["targets"][c["target"]] == c["target_rates"]
            assert manifest["spec"]["scale"] == c["scale"]
            assert manifest["spec"]["tolerance"] == 0.05
            program = restrict(c["program"])
            cases.append(
                {
                    "id": c["id"],
                    "case": c,
                    "original": measured,
                    "original_measurement_sha256": row["receipt"]["measurement_sha256"],
                    "program": program,
                    "changed": program != c["program"],
                }
            )
    if len(cases) != 180 or len({c["id"] for c in cases}) != 180:
        raise ValueError("expected 180 unique LLM finalists")
    for arm in ARMS:
        group = [c for c in cases if c["case"]["policy"] == arm]
        assert len(group) == 90
        verify_sources(read(Path(group[0]["case"]["root"]) / "manifest.json"), RUNTIMES[arm])
    index_path = ROOT / "results/mesh/power/repaired-references-v1/index.json"
    index = read(index_path)
    for target, entry in index["references"].items():
        path = ROOT / entry["path"]
        if sha(path) != entry["sha256"]:
            raise ValueError("repaired reference checksum mismatch")
        references[target] = read(path)
    result = {
        "version": "mesh-sink-sensitivity-v1",
        "intervention": "sink_period=8; sink_pause=min(max(original,0),3); all other fields unchanged",
        "selection": "Frozen power finalists (maximum-bin error, RMS, slot), no reselection after restriction",
        "scope": "Post-search sensitivity, not restricted-policy search. No new AUC or proposal-to-success claim.",
        "inputs": {
            str(ARCHIVE): sha(ARCHIVE),
            str(index_path): sha(index_path),
            str(Path(__file__).resolve()): sha(Path(__file__)),
        },
        "cases": cases,
        "references": references,
    }
    destination = OUT / "inventory.json"
    if destination.exists() and read(destination) != result:
        raise ValueError("frozen sensitivity inventory differs")
    write(destination, result)
    return result


def rtl(case, program, directory, runtime):
    if (directory / "measurement.json").exists():
        request = read(directory / "request.json")
        if request["program"] != program:
            raise ValueError("RTL resume program mismatch")
        return read(directory / "measurement.json")
    directory.mkdir(parents=True, exist_ok=True)
    manifest = read(Path(case["root"]) / "manifest.json")
    write(directory / "request.json", {"program": program, "manifest": manifest})
    module = (
        "agcws.designs.temporal_registry"
        if (runtime / "src/agcws/designs/temporal_registry.py").exists()
        else "agcws.pipeline.backends"
    )
    code = (
        "import json,sys; from pathlib import Path; "
        f"from {module} import backend; "
        'p=Path(sys.argv[1]); r=json.loads((p/"request.json").read_text()); '
        'm,hit=backend("mesh-temporal").measured(r["program"],p,r["manifest"]); '
        '(p/"measurement.json").write_text(json.dumps(m)+"\\n")'
    )
    with (directory / "run.log").open("a") as log:
        subprocess.run(
            [sys.executable, "-c", code, str(directory)],
            cwd=runtime,
            env=dict(os.environ, AGCWS_ROOT=str(runtime), PYTHONPATH=str(runtime / "src")),
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )
    return read(directory / "measurement.json")


def execute(item, reference):
    c = item["case"]
    directory = OUT / "cases" / item["id"]
    done = directory / "result.json"
    if done.exists():
        return read(done)
    directory.mkdir(parents=True, exist_ok=True)
    result = {
        "case_id": c["id"],
        "policy": c["policy"],
        "target": c["target"],
        "seed": c["seed"],
        "changed": item["changed"],
        "original_solved": c["activity_solved"],
        "original_max_bin_error": c["max_bin_error"],
        "original_power": compare_measurements(item["original"], reference),
    }
    try:
        if not item["changed"]:
            result.update(
                state="reused",
                valid=True,
                activity_solved=c["activity_solved"],
                rates=c["rates"],
                max_bin_error=c["max_bin_error"],
                loss=c["loss"],
                power=result["original_power"],
                original_measurement_sha256=item["original_measurement_sha256"],
            )
        else:
            runtime = RUNTIMES[c["policy"]]
            original = rtl(c, c["program"], directory / "original-rtl", runtime)
            if not original["valid"] or original["rates"] != c["rates"]:
                raise ValueError("original finalist does not reproduce frozen RTL rates")
            m = rtl(c, item["program"], directory / "restricted-rtl", runtime)
            write(
                directory / "rtl-complete.json",
                {
                    "valid": m["valid"],
                    "measurement_sha256": sha(directory / "restricted-rtl/measurement.json"),
                },
            )
            result.update(
                valid=m["valid"], rtl_measurement=str(directory / "restricted-rtl/measurement.json")
            )
            if not m["valid"]:
                result.update(state="invalid", activity_solved=False, rejection=m)
            else:
                worst = max_bin_error(m["rates"], c["target_rates"], c["scale"])
                loss = error(m["rates"], c["target_rates"], c["scale"])
                result.update(
                    rates=m["rates"], max_bin_error=worst, loss=loss, activity_solved=worst <= 0.05
                )
                manifest = read(Path(c["root"]) / "manifest.json")
                revised = {
                    **c,
                    "program": item["program"],
                    "rates": m["rates"],
                    "max_bin_error": worst,
                    "loss": loss,
                    "activity_solved": worst <= 0.05,
                    "replay_id": key(
                        {
                            "domain": c["domain"],
                            "program": item["program"],
                            "measurement": manifest["measurement_fingerprint"],
                        }
                    ),
                    "sensitivity": "mesh-sink-sensitivity-v1",
                    "original_measurement_sha256": item["original_measurement_sha256"],
                }
                plan = {
                    "version": "finalist-power-v1",
                    "selection": "Fixed original finalist with restricted sink; no reselection.",
                    "partial": False,
                    "inputs": {
                        str(directory / "restricted-rtl/measurement.json"): sha(
                            directory / "restricted-rtl/measurement.json"
                        ),
                        str(OUT / "inventory.json"): sha(OUT / "inventory.json"),
                    },
                    "cases": [revised],
                    "omitted": [],
                }
                plan["sha256"] = key(plan)
                write(directory / "plan.json", plan)
                attempts = sorted(p for p in directory.glob("power-attempt-*") if p.is_dir())
                successful = next((p for p in attempts if (p / "complete.json").exists()), None)
                if successful is None:
                    successful = directory / f"power-attempt-{len(attempts) + 1:03d}"
                    with (directory / f"{successful.name}.log").open("x") as log:
                        subprocess.run(
                            [
                                sys.executable,
                                "-m",
                                "agcws",
                                "power",
                                "run",
                                "--plan",
                                str(directory / "plan.json"),
                                "--case",
                                c["id"],
                                "--synthesis",
                                str(SYNTHESIS),
                                "--out",
                                str(successful),
                                "--runtime",
                                str(runtime),
                            ],
                            cwd=ROOT,
                            stdout=log,
                            stderr=subprocess.STDOUT,
                            check=True,
                        )
                path = successful / "measurement.json"
                if sha(path) != read(successful / "complete.json")["measurement_sha256"]:
                    raise ValueError("power receipt mismatch")
                result.update(
                    state="measured",
                    power=compare_measurements(read(path), reference),
                    power_measurement=str(path),
                    power_measurement_sha256=sha(path),
                )
    except Exception as exc:
        result.update(state="failed", error=repr(exc))
    write(done, result)
    print(json.dumps({k: result[k] for k in ("policy", "target", "seed", "state")}), flush=True)
    return result


def summarize(results):
    output = {}
    for arm in ARMS:
        output[arm] = {}
        for group, flat in (("nonflat", False), ("controls", True)):
            rows = [
                r
                for r in results
                if r["policy"] == arm and r["target"].endswith("flat_control") == flat
            ]
            available = [r for r in rows if r.get("power")]
            output[arm][group] = {
                "n": len(rows),
                "changed": sum(r["changed"] for r in rows),
                "states": dict(Counter(r["state"] for r in rows)),
                "original_solved": sum(r["original_solved"] for r in rows),
                "restricted_solved": sum(
                    r.get("activity_solved", False) for r in rows if r["state"] != "failed"
                ),
                "lost_matches": sum(
                    r["original_solved"] and not r.get("activity_solved", False)
                    for r in rows
                    if r["state"] != "failed"
                ),
                "gained_matches": sum(
                    not r["original_solved"] and r.get("activity_solved", False)
                    for r in rows
                    if r["state"] != "failed"
                ),
                "power_n": len(available),
                "original_mean_power_nrmse_matched": mean(
                    r["original_power"]["nrmse"] for r in available
                )
                if available
                else None,
                "restricted_mean_power_nrmse": mean(r["power"]["nrmse"] for r in available)
                if available
                else None,
            }
    return output


def main():
    global OUT
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    OUT = args.out.resolve()
    if not 1 <= args.workers <= 50:
        parser.error("--workers must be between 1 and 50")
    data = inventory()
    results = []
    unchanged = [c for c in data["cases"] if not c["changed"]]
    changed = [c for c in data["cases"] if c["changed"]]
    for c in unchanged:
        results.append(execute(c, data["references"][c["case"]["target"]]))

    def progress(active):
        write(
            OUT / "progress.json",
            {
                "version": data["version"],
                "updated_unix_s": time.time(),
                "total": 180,
                "completed": len(results),
                "states": dict(Counter(r["state"] for r in results)),
                "changed_total": len(changed),
                "running": active,
                "workers": args.workers,
            },
        )
        write(OUT / "partial-summary.json", summarize(results))

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        active = {
            pool.submit(execute, c, data["references"][c["case"]["target"]]): c["id"]
            for c in changed
        }
        progress(list(active.values()))
        while active:
            done, _ = concurrent.futures.wait(
                active, timeout=10, return_when=concurrent.futures.FIRST_COMPLETED
            )
            for f in done:
                active.pop(f)
                results.append(f.result())
            progress(list(active.values()))
    failures = [r for r in results if r["state"] == "failed"]
    write(
        OUT / "summary.json",
        {
            "version": data["version"],
            "scope": data["scope"],
            "complete": len(results) == 180,
            "all_executions_succeeded": not failures,
            "inventory_sha256": sha(OUT / "inventory.json"),
            "by_arm": summarize(results),
            "failures": failures,
            "cases": results,
        },
    )


if __name__ == "__main__":
    main()
