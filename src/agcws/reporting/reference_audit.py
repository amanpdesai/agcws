"""Offline cross-target audit of frozen calibration/bank construction evidence.

Only catalogued task evidence is eligible for selection; evaluation archives are
never candidate sources. Archived validity is evidence, not a fresh RTL/GLS check.
"""

import argparse
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from agcws.evidence import catalog
from agcws.evidence.packs import read_selected, sha
from agcws.designs.workloads.schedule import ScheduleContract, expand_schedule


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def maximum_error(rates, target, scale):
    if (len(rates) != 8 or len(target) != 8 or not math.isfinite(scale) or scale <= 0
            or any(not math.isfinite(x) or x < 0 for x in [*rates, *target])):
        raise ValueError("eight finite nonnegative bins and positive scale required")
    return max(abs(a - b) / scale for a, b in zip(rates, target))


def bundle(path):
    with gzip.open(path, "rt") as stream:
        records = json.load(stream)
    decoded = {}
    for name, record in records.items():
        if hashlib.sha256(record["text"].encode()).hexdigest() != record["sha256"]:
            raise ValueError(f"bundle member checksum differs: {name}")
        decoded[name] = json.loads(record["text"])
    return decoded, records


def validity(design, program, measurement):
    """Check archived functional acceptance plus explicit workload completion."""
    reasons = []
    profile = measurement.get("profile", {})
    if measurement.get("valid") is not True:
        reasons.append("archived functional/work validation failed or absent")
    if profile.get("activity_contract") != "known-bit-activity-v2":
        reasons.append("wrong or missing activity contract")
    if profile.get("remaining_unknown_bits", 0) != 0:
        reasons.append("unknown activity bits")
    work = profile.get("useful_work")
    if design in ("aes", "dma"):
        try:
            expand_schedule(program, ScheduleContract(64, 6000))
        except ValueError:
            reasons.append("invalid expanded work/idle schedule")
        if work != (64 if design == "aes" else 4096):
            reasons.append("fixed work differs")
    elif design == "ibex":
        allocation = measurement.get("allocation", [])
        if sum(allocation) != 4096 or not measurement.get("feedback", {}).get(
                "body_completed_before_deadline", False):
            reasons.append("4096 body instructions or deadline completion unverified")
    elif design == "mesh":
        required = sum(p["packets"] for p in program["phases"])
        if work != required or required < 64:
            reasons.append("packet completion/floor differs")
    elif design == "redmule":
        required = sum(p["jobs"] for p in program["phases"]) * program["size"] ** 3
        if work != required or required < 1024:
            reasons.append("GEMM completion/floor differs")
    return reasons


def candidate(design, program, measurement, source, member, member_sha):
    rates = measurement.get("profile", {}).get("window_rates", measurement.get("rates"))
    reasons = validity(design, program, measurement)
    if rates is None:
        reasons.append("no activity vector")
    else:
        try:
            maximum_error(rates, [0.] * 8, 1.)
        except (ValueError, TypeError):
            reasons.append("malformed activity vector")
            rates = None
    return {"program": program, "program_sha256": digest(program), "rates": rates,
            "eligible": not reasons, "exclusions": reasons,
            "archived_valid": measurement.get("valid") is True,
            "useful_work": measurement.get("profile", {}).get("useful_work"),
            "cache_id": measurement.get("cache_id"), "source": source,
            "member": member, "member_sha256": member_sha,
            "measurement_sha256": digest(measurement),
            "measurement_metadata": {k: measurement[k] for k in
                                     ("profile", "provenance", "allocation", "feedback")
                                     if k in measurement},
            "independence": "calibration/target-bank construction, not evaluated policy finalists"}


def audit(root, verify_selected=True):
    root = Path(root).resolve()
    result = {"version": "reference-repair-v1", "inputs": {}, "designs": {},
              "scope": "Exhaustive catalogued task bundles; no evaluation-run candidates, "
                       "new measurements, paid calls or frozen-file changes.",
              "limitations": ["Activity qualification does not certify matched power replay.",
                              "Bank construction is target-aware, not held-out ground truth.",
                              "Missing older Mesh calibration evidence is not inferred valid."]}

    def track(path):
        name = str(path.relative_to(root))
        result["inputs"][name] = sha(path)
        return name

    track(root / "results/index.json")
    for design in catalog.load(root)["designs"]:
        bank_path = catalog.design(root, design, "bank")
        config_path = catalog.design(root, design, "plan") / "config.json"
        bank = json.loads(bank_path.read_text())
        config = json.loads(config_path.read_text())
        track(bank_path)
        track(config_path)
        if bank["calibration"]["scale"] != config["scale"]:
            raise ValueError("bank/plan scale differs")
        targets = {k: v for k, v in config["targets"].items() if not k.endswith("flat_control")}
        requests = {f"{s}-{r['id']}": r["rates"] for s, part in bank["splits"].items()
                    for r in part["requests"]}
        if len(targets) != 8 or any(requests[k] != v for k, v in targets.items()):
            raise ValueError("expected eight frozen nonflat targets matching bank")
        directory = bank_path.parent / "calibration"
        path = directory / ("evidence.json.gz" if design == "mesh" else "inputs.json.gz")
        source = track(path)
        data, encoded = bundle(path)
        candidates = []

        def add(program, measurement, member, suffix=""):
            candidates.append(candidate(design, program, measurement, source,
                                        member + suffix, encoded[member]["sha256"]))

        if design == "mesh":
            for name, record in data.items():
                if name.startswith("panel/"):
                    add(record["program"], record["measurement"], name)
                elif name.startswith("cache/") and record.get("canonical_program"):
                    add(record["canonical_program"], record, name)
            for i, case in enumerate(data["manifest.json"]["cases"]):
                initial = case["initial"]
                add(initial["program"], initial, "manifest.json", f"#/cases/{i}/initial")
        else:
            for i, row in enumerate(data["replay/complete.json"]["results"]):
                add(row["program"], row["measurement"], "replay/complete.json",
                    f"#/results/{i}:{row['id']}")
            # This archive currently has only fixed-original rows; fail loudly if
            # future bundles add attempts that require separate measurement joins.
            if any(r["source"] != "fixed-original-witness"
                   for r in data["qualification/audited-attempts.json"]):
                raise ValueError("additional bank attempts require measurement joins")

        # Deduplicate identical programs AND measurements, retaining source order.
        unique = {}
        for c in candidates:
            unique.setdefault((c["program_sha256"], digest(c["rates"]), c["eligible"]), c)
        candidates = list(unique.values())
        power_path = catalog.design(root, design, "power")
        track(power_path)
        with gzip.open(power_path, "rt") as stream:
            powers = [json.loads(line) for line in stream]
        old = {}
        for collection in powers:
            if collection["bucket"] != f"references-{design}":
                continue
            for row in collection["records"]:
                case = row["case"]
                if case["target"] not in targets:
                    continue
                if case["scale"] != config["scale"] or case["target_rates"] != targets[case["target"]]:
                    raise ValueError("archived reference task differs")
                err = maximum_error(case["rates"], case["target_rates"], case["scale"])
                matches = [c for c in candidates if c["program_sha256"] == digest(case["program"])
                           and c["rates"] == case["rates"] and c["eligible"]]
                old[case["target"]] = {"max_bin_error": err, "activity_pass": err <= config["tolerance"],
                                       "task_evidence_joined": bool(matches), "case_id": case["id"],
                                       "source": case["reference_source"], "power_status": row["status"]}
        if len(old) != 8:
            raise ValueError("incomplete archived reference set")
        rows = []
        if not any(c["eligible"] for c in candidates):
            raise ValueError(f"{design}: no eligible candidates; inspect validity evidence")
        for name, target in targets.items():
            scored = sorted((maximum_error(c["rates"], target, config["scale"]),
                             c["program_sha256"], i)
                            for i, c in enumerate(candidates) if c["eligible"])
            error, _, index = scored[0]
            rows.append({"target": name, "target_rates": target, "old": old[name],
                         "best_candidate": index, "best_max_bin_error": error,
                         "qualified": error <= config["tolerance"],
                         "passing_candidates": sum(e <= config["tolerance"] for e, _, _ in scored),
                         "next_action": "bounded independent RTL then matched GLS/power validation"
                         if error <= config["tolerance"] else "fresh independent construction/search needed in audited pool"})
        checks = {}
        if verify_selected and design != "mesh":
            archive = directory / "fixed-replay"
            selected = {candidates[r["best_candidate"]]["member"].split(":")[-1]
                        for r in rows if r["qualified"]}
            names = [f"panel/{name}/result.json.gz" for name in sorted(selected)]
            if names:
                track(archive / "evidence.pack.json.gz")
                records = read_selected(archive, names)
                for name, raw in records.items():
                    decoded = json.loads(gzip.decompress(raw))
                    original = next(r for r in data["replay/complete.json"]["results"]
                                    if r["id"] == decoded["id"])
                    if decoded != original:
                        raise ValueError("selected tar evidence differs from compact bundle")
                    checks[name] = hashlib.sha256(raw).hexdigest()
        result["designs"][design] = {
            "domain": config["domain"], "scale": config["scale"], "tolerance": config["tolerance"],
            "measurement_manifest": (data["manifest.json"]["measurement"] if design == "mesh"
                                     else data["reference/manifest.json"]),
            "archived_reference_runtime": [p["collection"] for p in powers
                                           if p["bucket"] == f"references-{design}"],
            "candidate_records": len(candidates), "eligible_candidates": sum(c["eligible"] for c in candidates),
            "exclusion_counts": dict(Counter(reason for c in candidates for reason in c["exclusions"])),
            "old_activity_coverage": sum(r["old"]["activity_pass"] for r in rows),
            "attainable_independent_activity_coverage": sum(r["qualified"] for r in rows),
            "selected_tar_members_verified": checks, "targets": rows, "candidates": candidates}
        if design == "mesh":
            # Old-bank witnesses carry validity labels but lack complete joined
            # measurement records. Preserve their bounds without upgrading them.
            witnessed = []
            for row in bank["witnesses"]:
                w = row["witness"]
                if w is None:
                    continue
                witnessed.append({"id": row["id"], "source": row["source"],
                                  "program": w["program"], "program_sha256": digest(w["program"]),
                                  "rates": w["rates"], "archived_valid": w.get("valid"),
                                  "errors": {k: maximum_error(w["rates"], t, config["scale"])
                                             for k, t in targets.items()},
                                  "qualification": "bank label only; full measurement join required"})
            result["designs"][design]["bank_witness_inventory"] = witnessed
    result["totals"] = {key: sum(d[key] for d in result["designs"].values()) for key in
                        ("candidate_records", "eligible_candidates", "old_activity_coverage",
                         "attainable_independent_activity_coverage")}
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--skip-tar-verification", action="store_true")
    args = parser.parse_args(argv)
    report = audit(args.root, not args.skip_tar_verification)
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "audit.json").open("x") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    handoff = {"scope": report["scope"], "totals": report["totals"], "designs": {}}
    for design, record in report["designs"].items():
        handoff["designs"][design] = {
            k: record[k] for k in ("domain", "scale", "tolerance", "measurement_manifest",
                                  "archived_reference_runtime")}
        handoff["designs"][design]["targets"] = [
            {**row, "candidate": record["candidates"][row["best_candidate"]]}
            for row in record["targets"]]
    with (args.out / "best-candidates.json").open("x") as stream:
        json.dump(handoff, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps(report["totals"]))


if __name__ == "__main__":
    main()
