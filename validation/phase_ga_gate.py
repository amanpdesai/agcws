"""Execute the frozen seven-program equivalence gate through the maintained evaluator."""

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

from agcws.pipeline import engine
from agcws.pipeline.ibex.cache import measured
from agcws.pipeline.ibex.program import canonical
from agcws.pipeline.storage import ensure, write
from analysis.accounting_audit import equivalent, read
from analysis.accounting_math import rms
from analysis.control_readiness import fingerprint


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(old, new, old_run, new_run, targets, scale):
    checks = {}
    for field in ("valid", "stage", "reason", "allocation"):
        checks[field] = old[field] == new[field]
    old_profile, new_profile = old["profile"], new["profile"]
    for field in (
        "window_bit_transitions",
        "window_rates",
        "clock_edges",
        "period_ticks",
        "begin_tick",
        "end_tick",
        "timescale",
        "selected_identifiers",
        "scope",
        "exclusions",
        "unknown_events",
        "markers",
        "retired_instructions",
    ):
        checks["profile." + field] = old_profile[field] == new_profile[field]
    checks["assembly"] = old_run["assembly"] == new_run["assembly"]
    checks["reference_state"] = (
        old_run["functional"]["expected"] == new_run["functional"]["expected"]
    )
    checks["functional_ok"] = (
        old_run["functional"]["functional_ok"] is new_run["functional"]["functional_ok"] is True
    )
    checks["marker_pcs"] = (
        old_run["functional"]["marker_pcs"] == new_run["functional"]["marker_pcs"]
    )
    losses = []
    for target in targets:
        previous = rms(old_profile["window_rates"], target["rates"], scale)
        current = rms(new_profile["window_rates"], target["rates"], scale)
        checks["loss." + target["id"]] = equivalent(previous, current)
        losses.append({"target": target["id"], "historical": previous, "replay": current})
    return {"passed": all(checks.values()), "checks": checks, "losses": losses}


def run(repo, historical, binary, gate, evidence):
    ready = read(repo / "results/evidence_extension_v1/control_readiness.json")
    frozen = read(repo / "results/evidence_extension_v1/freeze.json")
    for name, expected in frozen["files_sha256"].items():
        if digest(repo / name) != expected:
            raise ValueError("frozen readiness input changed: " + name)
    for name, expected in ready["source_sha256"].items():
        if digest(repo / name) != expected:
            raise ValueError("offline-checked source changed: " + name)
    parent = read(historical / "parent_manifest.json")
    original = read(historical / "manifest.json")
    targets = read(historical / "targets.json")
    measurement = parent["measurement"]
    image = measurement["image_id"]
    actual = {
        "image_id": subprocess.check_output(
            ["docker", "image", "inspect", image, "--format", "{{.Id}}"], text=True
        ).strip(),
        "binary_sha256": digest(binary),
        "ibex_commit": subprocess.check_output(
            ["git", "-C", str(repo / "third_party/ibex"), "rev-parse", "HEAD"], text=True
        ).strip(),
    }
    if any(actual[k] != measurement[k] for k in actual):
        raise ValueError("runtime identity differs; do not substitute")
    dirty = subprocess.check_output(
        ["git", "-C", str(repo / "third_party/ibex"), "status", "--porcelain"], text=True
    )
    if dirty:
        raise ValueError("Ibex working tree is not the pinned revision")
    tool_probe = (
        "import hashlib,json,shutil,subprocess,sys; "
        "names=['riscv64-unknown-elf-gcc','riscv64-unknown-elf-objcopy',"
        "'riscv64-unknown-elf-nm','fst2vcd']; "
        "paths={n:shutil.which(n) for n in names}; "
        "assert all(paths.values()); "
        "print(json.dumps({'python':sys.version,'tools':{n:{'path':p,"
        "'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest()} "
        "for n,p in paths.items()}}))"
    )
    tools = json.loads(
        subprocess.check_output(
            [
                "docker",
                "run",
                "--rm",
                "--read-only",
                "--network",
                "none",
                "--entrypoint",
                "python3",
                image,
                "-c",
                tool_probe,
            ],
            text=True,
        )
    )
    spec = {
        "name": "phase-ga-robustness-v1",
        "domain": "ibex-temporal",
        "targets": {t["id"]: t["rates"] for t in targets},
        "seeds": original["seeds"],
        "policies": ["phase-ga"],
        "budget": 128,
        "batch_size": 2,
        "scale": original["scale"],
        "tolerance": original["tolerance"],
        "binary": str(binary),
        "image": image,
        "max_workers": 1,
        "cost_ceiling_usd": 1,
    }
    evidence.mkdir(parents=True, exist_ok=False)
    write(evidence / "spec.json", spec)
    manifest = engine.prepare(repo, evidence / "spec.json", gate)
    write(evidence / "gate_manifest.json", manifest)
    identity = {
        "runtime": actual,
        "container_tools": tools,
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "ibex_dirty": False,
        "selection": ready["live_replay_selection"],
        "inputs_sha256": {
            "protocol": digest(repo / "docs/PHASE_GA_ROBUSTNESS_V1.md"),
            "readiness": digest(repo / "results/evidence_extension_v1/control_readiness.json"),
            "historical_manifest": digest(historical / "manifest.json"),
            "historical_targets": digest(historical / "targets.json"),
            "historical_parent": digest(historical / "parent_manifest.json"),
            "gate_source": digest(Path(__file__)),
        },
        "started_unix": time.time(),
        "historical_measurement": measurement,
    }
    write(evidence / "runtime_and_selection.json", identity)
    print(
        json.dumps({"gate": "runtime verified", "programs": len(identity["selection"])}), flush=True
    )
    cases = []
    try:
        for item in identity["selection"]:
            identifier = item["cache_id"]
            old_dir = historical / "evaluations" / identifier
            program = read(old_dir / "program.json.gz")
            if fingerprint(canonical(program)) != item["program_sha256"]:
                raise ValueError("frozen selected program changed")
            old = read(old_dir / "result.json.gz")
            engine.verify_inputs(repo, gate)
            current, hit = measured(program, gate, manifest["measurement_fingerprint"], image)
            if hit:
                raise ValueError("gate must measure every selected program freshly")
            new_dir = gate / "cache" / current["cache_id"]
            if not current["valid"]:
                case = {"passed": False, "checks": {"valid": False}, "replay": current}
            else:
                import gzip

                old_run = {
                    "assembly": gzip.decompress((old_dir / "run/program.S.gz").read_bytes()),
                    "functional": read(old_dir / "run/functional.json.gz"),
                }
                new_run = {
                    "assembly": (new_dir / "run/program.S").read_bytes(),
                    "functional": read(new_dir / "run/functional.json"),
                }
                case = compare(old, current, old_run, new_run, targets, spec["scale"])
                case["profiles"] = {"historical": old["profile"], "replay": current["profile"]}
            case.update(
                historical_cache_id=identifier,
                replay_cache_id=current["cache_id"],
                origins=item["origins"],
                replay_s=current["evaluation_s"],
            )
            write(evidence / (identifier + ".json"), case)
            cases.append(case)
            print(
                json.dumps(
                    {
                        "case": identifier,
                        "passed": case["passed"],
                        "completed": len(cases),
                        "seconds": current["evaluation_s"],
                    }
                ),
                flush=True,
            )
            if not case["passed"]:
                raise ValueError("equivalence mismatch; extension halted")
        engine.verify_inputs(repo, gate)
        ensure(
            evidence / "complete.json",
            {"passed": True, "cases": len(cases), "completed_unix": time.time()},
        )
    except Exception as exc:
        write(
            evidence / "failure.json",
            {"error": repr(exc), "completed_cases": len(cases), "time_unix": time.time()},
        )
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("historical", "binary", "gate", "evidence"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        parser.error("--execute required; no measurements launched")
    run(
        Path.cwd().resolve(),
        args.historical.resolve(),
        args.binary.resolve(strict=True),
        args.gate.resolve(),
        args.evidence.resolve(),
    )


if __name__ == "__main__":
    main()
