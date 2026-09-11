"""Offline record/intent inspection; no simulation or provider access."""

import argparse
import collections
import json
import statistics
from pathlib import Path

from agcws.pipeline.ibex.program import interpret
from agcws.pipeline.ibex.prompt import payload
from analysis.solution_audit import digest, read, select, trials


def execution_summary(row):
    execution = row.get("execution")
    if not row["valid"] or not execution:
        return None
    bins = []
    for b in execution["bins"]:
        phases = b["retired_by_phase"]
        total = sum(phases.values())
        wait = sum(
            n for phase, n in phases.items() if phase.endswith("_poll") or phase == "body_complete"
        )
        bins.append(
            {
                "retired": total,
                "wait_retired": wait,
                "wait_retired_fraction": wait / total,
                "nonzero_divisor": b["divide_nonzero_divisor"],
                "zero_divisor": b["divide_zero_divisor"],
                "zero_numerator": b["divide_zero_numerator"],
            }
        )
    return {
        "bins": bins,
        "body_completion_cycles": row["feedback"]["body_completion_cycles"],
        "wait_retired_fraction": sum(b["wait_retired"] for b in bins)
        / sum(b["retired"] for b in bins),
        "phases": execution["phases"],
    }


def inspect(root, selection, scratch):
    if select(root) != selection:
        raise ValueError("frozen selection or inputs changed")
    manifest = read(root / "manifest.json")
    targets = {t["id"]: t for t in read(root / "targets.json")}
    witnesses = read(root / "witnesses.json")
    witness_programs = {json.dumps(w["program"], sort_keys=True) for w in witnesses}
    cases = []
    checks = collections.Counter()
    failures = []
    payload_hashes = {}
    arm_best = collections.defaultdict(list)
    for cell in selection["cells"]:
        rows, paths = trials(root, cell)
        directory = paths[0].parent.parent
        for offset in range(0, 128, 2):
            path = directory / f"{offset + 1:03}" / "input.json.gz"
            sent = read(path)
            if sent["payload"] is None:
                continue
            text = sent["payload"]
            value = json.loads(text)
            checks["payloads"] += 1
            payload_hashes[str(path.relative_to(root))] = digest(path)
            expected = payload(
                rows[:offset],
                {
                    "profile": targets[cell["target"]]["rates"],
                    "scale": manifest["scale"],
                    "tolerance": manifest["tolerance"],
                },
                2,
                True,
            )
            if expected != text:
                failures.append({"cell": cell, "offset": offset, "check": "payload reconstruction"})
            for h in value["history"]:
                checks["history_rows"] += 1
                if not 1 <= h["slot"] <= offset:
                    failures.append({"check": "future/out-of-cell slot", "path": str(path)})
                elif any(rows[h["slot"] - 1].get(k) != v for k, v in h.items()):
                    failures.append(
                        {"check": "history content mismatch", "path": str(path), "slot": h["slot"]}
                    )
                if json.dumps(h["program"], sort_keys=True) in witness_programs:
                    checks["exact_witness_in_history"] += 1
            for term in (
                "witness_cache_id",
                "witness_slot",
                "construction_seed",
                "scheduled-four-phase",
            ):
                if term in text:
                    failures.append(
                        {"check": "privileged-term lead", "term": term, "path": str(path)}
                    )
        selected = {slot for slot in cell["roles"].values() if slot is not None}
        for slot in sorted(selected):
            row = rows[slot - 1]
            checks["selected_records"] += 1
            role = [k for k, v in cell["roles"].items() if v == slot]
            batch = directory / f"{((slot - 1) // 2) * 2 + 1:03}"
            decoded = read(batch / "decoded.json.gz")
            summary = execution_summary(row)
            case = {
                "target": cell["target"],
                "seed": cell["seed"],
                "arm": cell["arm"],
                "slot": slot,
                "roles": role,
                "detailed": cell["detailed"]
                or (cell.get("supplemental_first_solve", False) and "first_solve" in role),
                "program": row["program"],
                "valid": row["valid"],
                "stage": row["stage"],
                "reason": row["reason"],
                "loss": row["loss"],
                "rates": row["rates"],
                "allocation": row["allocation"],
                "prediction": row["prediction"],
                "prediction_assessment": row["prediction_assessment"],
                "hypothesis": decoded.get("hypothesis"),
                "execution": summary,
                "cache_id": row.get("cache_id"),
            }
            if row.get("cache_id"):
                waveform = scratch / "cache" / row["cache_id"] / "run/sim.fst"
                case["waveform_present"] = waveform.is_file()
            if row["valid"]:
                base = root / "evaluations" / row["cache_id"] / "run"
                functional = read(base / "functional.json.gz")
                profile = read(base / "profile.json.gz")
                expected = interpret(row["program"])
                checks["functional_references_checked"] += 1
                if expected != functional["expected"]:
                    failures.append({"check": "reference mismatch", "case": case["cache_id"]})
                if expected["useful_work"] != 4096 or sum(row["allocation"]) != 4096:
                    failures.append({"check": "work allocation", "case": case["cache_id"]})
                if (
                    profile["window_rates"] != row["rates"]
                    or profile["end_tick"] - profile["begin_tick"] != 400000
                ):
                    failures.append({"check": "window/rates", "case": case["cache_id"]})
                case["reference_operations"] = expected["operations"]
                case["semantic_registers_unchanged"] = (
                    expected["registers"] == row["program"]["registers"]
                )
                case["profile_sha256"] = digest(base / "profile.json.gz")
                if "best" in role:
                    arm_best[cell["arm"]].append(summary["wait_retired_fraction"])
            cases.append(case)
    return {
        "checks": dict(checks),
        "failures": failures,
        "cases": cases,
        "payload_sha256": payload_hashes,
        "best_wait_retired_fraction": {
            a: {"mean": statistics.mean(v), "min": min(v), "max": max(v)}
            for a, v in arm_best.items()
        },
        "limits": [
            "Wait fractions count retired instructions, not cycles, energy or useful computation.",
            "Reference recomputation uses the migrated interpreter; not an independent functional oracle.",
            "Payload reconstruction uses the migrated frozen-equivalent builder; literal matching does not rule out conceptual alignment.",
            "Emitted explanations are observable claims, not access to private model reasoning.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = inspect(
        Path("results/nonflat_temporal_v1"),
        read(Path("results/solution_audit_v1/selection.json")),
        Path("out/nonflat-temporal-v1"),
    )
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("cases", "payload_sha256")}))


if __name__ == "__main__":
    main()
