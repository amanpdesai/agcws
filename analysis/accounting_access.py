"""Supplemental transport, input visibility and rejection audit; no policy helpers."""

import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path

import jsonschema

from analysis.accounting_audit import canonical, digest, read


def audit(root, scratch):
    issues, counts, local_hashes, invalid = [], collections.Counter(), {}, []
    references = []

    def check(ok, name, where):
        counts[name] += 1
        if not ok:
            issues.append({"check": name, "location": where})

    expected_local = set()
    core_keys = set()
    for batch in sorted((root / "panel").glob("*/*/*/batches/*")):
        rel = batch.relative_to(root)
        saved = read(batch / "input.json.gz")
        trials = read(batch / "trials.json.gz")
        value = json.loads(saved["payload"]) if saved["payload"] else None
        if value:
            schema = value["schema"]
            validator = jsonschema.Draft202012Validator(schema)
            core_keys.add(hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest())
        else:
            # The workload schema is identical across observed model payloads;
            # CPU proposals are validated in a second pass below with that schema.
            validator = None
        for p in batch.iterdir():
            if p.suffix != ".gz":
                raise ValueError("unexpected uncompressed batch")
            original = scratch / p.relative_to(root).with_suffix("")
            name = str(original.relative_to(scratch))
            if original.exists():
                checksum = hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest()
                local_hashes[name] = digest(original)
                check(local_hashes[name] == checksum, "raw_local_archive_bytes", name)
            else:
                issues.append({"check": "raw_local_file_missing", "location": name})
            if original.name in ("request_started.json", "response.json"):
                expected_local.add(name)
        if value:
            visible = {h["slot"] for h in value["history"]}
            for trial in trials:
                note = trial.get("prediction")
                if note and note["reference_slot"] not in visible:
                    counts["prediction_reference_not_in_compact_history"] += 1
                    references.append(
                        {
                            "batch": str(rel),
                            "slot": trial["slot"],
                            "reference_slot": note["reference_slot"],
                            "prediction_error": trial["prediction_error"],
                            "scorable": trial["prediction_assessment"]["scorable"],
                            "notebook_row_visible": any(
                                n["slot"] == note["reference_slot"]
                                for n in value["experiment_notebook"]
                            ),
                            "notebook_reference_visible": any(
                                (n.get("prediction") or {}).get("reference_slot")
                                == note["reference_slot"]
                                for n in value["experiment_notebook"]
                            ),
                        }
                    )
                if trial.get("canonical_program"):
                    check(
                        canonical(trial["program"]) == trial["canonical_program"],
                        "only_integral_number_canonicalization",
                        str(rel),
                    )
            response = read(batch / "response.json.gz")
            counts["unknown_usage_responses"] += response["usage_unknown"]
            counts["known_usage_responses"] += not response["usage_unknown"]
            for reason in response["finish_reasons"]:
                counts["finish_" + reason] += 1
            for trial in trials:
                errors = list(validator.iter_errors(canonical(trial["program"])))
                check(
                    bool(errors) == (trial["stage"] in ("SCHEMA", "API")),
                    "independent_schema_rejection",
                    str(rel) + f"/{trial['slot']}",
                )
                if not trial["valid"]:
                    invalid.append(
                        {
                            "batch": str(rel),
                            "slot": trial["slot"],
                            "stage": trial["stage"],
                            "reason": trial["reason"],
                            "schema_errors": [e.message for e in errors],
                        }
                    )
    if len(core_keys) != 1:
        raise ValueError("workload schema varied")
    for batch in sorted((root / "panel").glob("*/*/phase-random/batches/*")):
        for trial in read(batch / "trials.json.gz"):
            check(
                not list(
                    jsonschema.Draft202012Validator(schema).iter_errors(canonical(trial["program"]))
                ),
                "cpu_same_schema",
                str(batch.relative_to(root)) + f"/{trial['slot']}",
            )
    actual_local = {
        str(p.relative_to(scratch))
        for name in ("request_started.json", "response.json")
        for p in scratch.rglob(name)
    }
    check(actual_local == expected_local, "no_extra_local_request_response_paths", "scratch")
    for directory in sorted((root / "panel").glob("*/*/*")):
        rel = directory.relative_to(root)
        archived = read(directory / "complete.json")
        check(read(scratch / rel / "complete.json") == archived, "local_terminal_cell", str(rel))
        ident = read(scratch / rel / "identity.json")
        check(
            ident
            == {"cell": archived["cell"], "search_sha256": digest(root / "search_manifest.json")},
            "local_cell_identity",
            str(rel),
        )
    check(
        read(scratch / "complete.json")
        == read(root / "complete.json")
        == {"cells": 36, "slots": 4608},
        "terminal_panel",
        "complete",
    )
    log = scratch / "service.log"
    progress = []
    for line in log.read_text().splitlines():
        if line.startswith("{"):
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if "progress" in event:
                progress.append(
                    (json.dumps(event["progress"], sort_keys=True), event["completed_slots"])
                )
    expected_progress = {
        (json.dumps(cell, sort_keys=True), slot)
        for cell in read(root / "search_manifest.json")["cells"]
        for slot in range(2, 129, 2)
    }
    check(set(progress) == expected_progress, "service_progress_coverage", "service.log")
    for archived in (root / "smoke").rglob("*.json*"):
        local = scratch / archived.relative_to(root)
        if local.suffix == ".gz":
            local = local.with_suffix("")
        check(
            local.exists() and read(local) == read(archived),
            "separate_smoke_records",
            str(archived.relative_to(root)),
        )
    return {
        "checks_and_diagnostics": dict(counts),
        "discrepancies": issues,
        "invalid_model_slots": invalid,
        "prediction_references_outside_compact_history": references,
        "raw_local_sha256": local_hashes,
        "service_log_sha256": digest(log),
        "progress_events": len(progress),
        "unique_progress_events": len(set(progress)),
        "extra_local_request_paths": sorted(actual_local - expected_local),
        "missing_local_request_paths": sorted(expected_local - actual_local),
        "limits": [
            "Local records are corroboration, not an independent provider invoice or HTTP capture.",
            "SDK source sets attempts=1; recorded request count cannot prove the absence of provider-internal attempts.",
            "Schema compliance does not establish meaningful application progress or causal reasoning.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.archive, args.scratch)
    data = (json.dumps(result, indent=2) + "\n").encode()
    with args.out.open("xb") as output:
        output.write(gzip.compress(data, mtime=0) if args.out.suffix == ".gz" else data)
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k
                not in (
                    "invalid_model_slots",
                    "raw_local_sha256",
                    "prediction_references_outside_compact_history",
                )
            },
            indent=2,
        )
    )

    if result["discrepancies"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
