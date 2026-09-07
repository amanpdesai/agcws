"""Reconcile container replay records with raw reports and original finalists."""

import json
from pathlib import Path

from analysis.matched_power import parse_report
from maintenance.trace_store import digest


def audit(root=Path("results/container_window_replay_v1")):
    verified = 0
    for design in ("aes", "dma"):
        case = root / design
        record = json.loads((case / "verification.json").read_text())
        power = json.loads((case / "windows/power.json").read_text())
        original_path = (
            Path("results/windowed_power_v1/finalists")
            / record["case"]["replay_id"]
            / "power.json"
        )
        original = json.loads(original_path.read_text())
        assert record["uid"] != 0 and record["image_only"]
        assert record["input_manifest_sha256"] == digest(root / "inputs.json")
        assert record["packages_sha256"] == digest(case / "python-packages.txt")
        assert power["grid"] == original["grid"]
        assert power["switching_additivity_pass"]
        assert len(power["windows"]) == len(original["windows"]) == 8
        assert len(record["comparison"]) == 36
        assert record["all_power_components_match"]
        for name, checksum in power["artifact_sha256"].items():
            assert digest(case / "windows" / name) == checksum
        for comparison in record["comparison"]:
            name, metric = comparison["window"], comparison["metric"]
            raw = parse_report((case / "windows" / f"{name}.rpt").read_text())
            expected = next(
                r for r in [original["full"], *original["windows"]] if r["name"] == name
            )
            assert comparison["matches"]
            assert comparison["container"] == raw[metric]
            assert comparison["host"] == expected[metric]
            verified += 1
    return {
        "designs": 2,
        "verified_components": verified,
        "scope": "Compact report reconciliation, not a new simulation.",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
