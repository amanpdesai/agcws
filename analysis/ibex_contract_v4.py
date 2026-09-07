"""Check every fixed-context call and recompute contract readiness from raw output."""

import argparse
import json
import math
import shutil
from pathlib import Path

from agcws.provenance import file_sha256
from experiments.ibex_temporal_v4.contract import decode
from experiments.ibex_temporal_v4.evaluate import write


def verify(root):
    manifest = json.loads((root / "manifest.json").read_text())
    if (
        len(manifest["calls"]) != 24
        or len({c["name"] for c in manifest["calls"]}) != 24
    ):
        raise ValueError("expected 24 unique declared calls")
    if {p.stem for p in (root / "calls").glob("*.json")} != {
        c["name"] for c in manifest["calls"]
    }:
        raise ValueError("missing or extra call artifacts")
    for path, digest in manifest["sources"].items():
        if file_sha256(root / "sources" / path) != digest:
            raise ValueError("frozen source copy mismatch")
    if file_sha256(root / "schema.json") != manifest["schema_sha256"]:
        raise ValueError("native schema hash mismatch")
    reports = {}
    for arm in ("original", "contract"):
        report = dict.fromkeys(
            (
                "calls",
                "requested_slots",
                "schema_valid",
                "complete_response_adherence",
                "unknown_usage",
                "api_errors",
                "tokens_in",
                "tokens_out",
                "est_cost_usd",
            ),
            0,
        )
        for call in (c for c in manifest["calls"] if c["arm"] == arm):
            if (
                file_sha256(root / "inputs" / f"{call['name']}.json")
                != call["payload_sha256"]
            ):
                raise ValueError("input payload mismatch")
            r = json.loads((root / "calls" / f"{call['name']}.json").read_text())
            decoded = decode(r["raw_text"], 2)
            if r["call"] != call or decoded != r["decoded"]:
                raise ValueError("call identity or raw decoding mismatch")
            report["calls"] += 1
            report["requested_slots"] += 2
            report["schema_valid"] += sum(
                s["canonical"] is not None for s in decoded["slots"]
            )
            report["complete_response_adherence"] += decoded["response_error"] is None
            report["unknown_usage"] += r["usage_unknown"]
            report["api_errors"] += "exception" in r
            for key in ("tokens_in", "tokens_out", "est_cost_usd"):
                report[key] += r[key]
        reports[arm] = report
    c = reports["contract"]
    aggregate = {
        "arms": reports,
        "ready": c["schema_valid"] / c["requested_slots"] >= 0.9
        and c["unknown_usage"] == 0
        and c["api_errors"] == 0,
        "scope": "static response-contract development; no hardware/search-quality claim",
    }
    recorded = json.loads((root / "aggregate.json").read_text())
    for arm in reports:
        expected = recorded["arms"][arm]["est_cost_usd"]
        if not math.isclose(
            reports[arm]["est_cost_usd"], expected, rel_tol=0, abs_tol=1e-12
        ):
            raise ValueError("cost arithmetic mismatch")
        reports[arm]["est_cost_usd"] = expected
    if aggregate != recorded:
        raise ValueError("aggregate does not match raw evidence")
    index = json.loads((root / "sha256.json").read_text())
    actual = {
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and p.name != "sha256.json"
    }
    if actual != set(index):
        raise ValueError("hash inventory differs")
    for name, digest in index.items():
        p = root / name
        if not p.resolve().is_relative_to(root.resolve()) or file_sha256(p) != digest:
            raise ValueError("archive hash or path mismatch")
    return {
        "calls_verified": 24,
        "slots_verified": 48,
        "files_verified": len(index),
        "ready": aggregate["ready"],
    }


def archive(root):
    manifest = json.loads((root / "manifest.json").read_text())
    for path, digest in manifest["sources"].items():
        if file_sha256(Path(path)) != digest:
            raise ValueError(f"frozen source changed: {path}")
        target = root / "sources" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    write(
        root / "sha256.json",
        {
            str(p.relative_to(root)): file_sha256(p)
            for p in sorted(root.rglob("*"))
            if p.is_file() and p.name != "sha256.json"
        },
    )
    return verify(root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--archive", action="store_true")
    args = parser.parse_args()
    print(json.dumps((archive if args.archive else verify)(args.root), indent=2))
