"""Capture and verify the fixed-finalist Mesh sensitivity without local waveforms."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from agcws.core import config
from agcws.evaluation.power.mesh_sensitivity import restrict, summarize
from agcws.evidence.power import load as load_power
from agcws.reporting.metrics import error, max_bin_error
from agcws.reporting.power_reference import compare_measurements

DESTINATION = Path("results/mesh/sink-sensitivity")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def capture(source, destination):
    inventory = json.loads((source / "inventory.json").read_text())
    summary = json.loads((source / "summary.json").read_text())
    if not summary["complete"] or not summary["all_executions_succeeded"]:
        raise ValueError("sensitivity collection is not complete")
    files = {}

    def add(path):
        raw = path.read_bytes()
        files[str(path.relative_to(source))] = {"text": raw.decode(), "sha256": digest(raw)}

    for name in ("run.py", "inventory.json", "summary.json"):
        add(source / name)
    for row in summary["cases"]:
        if not row["changed"]:
            continue
        directory = source / "cases" / row["case_id"]
        for name in (
            "original-rtl/measurement.json",
            "restricted-rtl/measurement.json",
            "restricted-rtl/request.json",
            "plan.json",
            "result.json",
        ):
            add(directory / name)
        for failed in directory.glob("result.failed-*.json"):
            add(failed)
        measurement = Path(row["power_measurement"])
        for path in (measurement, measurement.parent / "complete.json"):
            add(path)
        for folder in ("power", "gls"):
            for path in (measurement.parent / folder).iterdir():
                if path.suffix in (".json", ".rpt", ".tcl"):
                    add(path)
    record = {
        "version": "mesh-sink-sensitivity-evidence-v1",
        "files": files,
        "source_root": str(source),
        "external_inputs": {
            "results/mesh/power/measurements.jsonl.gz": inventory["inputs"][
                str(config.ROOT / "results/mesh/power/measurements.jsonl.gz")
            ]
        },
    }
    ref_index = config.ROOT / "results/mesh/tasks/references/index.json"
    record["external_inputs"][str(ref_index.relative_to(config.ROOT))] = digest(
        ref_index.read_bytes()
    )
    raw = gzip.compress((json.dumps(record, sort_keys=True) + "\n").encode(), mtime=0)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / "evidence.json.gz"
    if path.exists() and path.read_bytes() != raw:
        raise ValueError("frozen sensitivity evidence changed")
    path.write_bytes(raw)


def verify(destination, root=config.ROOT):
    path = destination / "evidence.json.gz"
    archive = json.loads(gzip.decompress(path.read_bytes()))
    files = archive["files"]
    for name, item in files.items():
        if digest(item["text"].encode()) != item["sha256"]:
            raise ValueError(f"evidence checksum differs: {name}")

    def read(name):
        return json.loads(files[name]["text"])

    for name, expected in archive["external_inputs"].items():
        if digest((root / name).read_bytes()) != expected:
            raise ValueError("original archive checksum differs")
    inventory, summary = read("inventory.json"), read("summary.json")
    assert summary["inventory_sha256"] == files["inventory.json"]["sha256"]
    assert (
        inventory["inputs"][str(Path(archive["source_root"]) / "run.py")]
        == files["run.py"]["sha256"]
    )
    buckets, measurements = load_power(root, 'mesh')
    originals = {row['case']['id']:row for bucket in buckets for row in bucket['records']}
    ref_index = json.loads(
        (root / "results/mesh/tasks/references/index.json").read_text()
    )
    for target, entry in ref_index["references"].items():
        assert inventory["references"][target] == measurements[entry['case_id']]
    for row in originals.values():
        if row["case"].get("role") == "power_reference" and row["case"]["target"].endswith(
            "flat_control"
        ):
            assert inventory["references"][row["case"]["target"]] == json.loads(
                row["raw_measurement"]
            )
    items = {item["id"]: item for item in inventory["cases"]}
    assert len(items) == len(summary["cases"]) == 180
    assert len({r["case_id"] for r in summary["cases"]}) == 180
    for row in summary["cases"]:
        item = items[row["case_id"]]
        case = item["case"]
        original = originals[row["case_id"]]
        assert case == original["case"]
        assert digest(original["raw_measurement"].encode()) == item["original_measurement_sha256"]
        assert json.loads(original["raw_measurement"]) == item["original"]
        assert item["program"] == restrict(case["program"])
        assert row["changed"] == (item["program"] != case["program"])
        prefix = "cases/" + row["case_id"] + "/"
        reference = inventory["references"][case["target"]]
        assert row["original_power"] == compare_measurements(item["original"], reference)
        if row["changed"]:
            assert row["state"] == "measured"
            original_rtl = read(prefix + "original-rtl/measurement.json")
            rtl = read(prefix + "restricted-rtl/measurement.json")
            assert original_rtl["valid"] and original_rtl["rates"] == case["rates"]
            assert rtl["valid"] and rtl["rates"] == row["rates"]
            assert read(prefix + "restricted-rtl/request.json")["program"] == item["program"]
            name = str(Path(row["power_measurement"]).relative_to(archive["source_root"]))
            measured = read(name)
            assert files[name]["sha256"] == row["power_measurement_sha256"]
            assert (
                read(str(Path(name).parent / "complete.json"))["measurement_sha256"]
                == files[name]["sha256"]
            )
            assert measured["activity"]["program"] == item["program"]
            assert measured["activity"]["rates"] == row["rates"]
            assert measured["power"]["switching_additivity_pass"]
        else:
            assert row["state"] == "reused" and row["rates"] == case["rates"]
            measured = item["original"]
        assert row["max_bin_error"] == max_bin_error(
            row["rates"], case["target_rates"], case["scale"]
        )
        assert row["loss"] == error(row["rates"], case["target_rates"], case["scale"])
        assert row["activity_solved"] == (row["max_bin_error"] <= 0.05)
        assert row["power"] == compare_measurements(measured, reference)
    computed = summarize(summary["cases"])
    assert computed == summary["by_arm"]
    return {
        "version": archive["version"],
        "evidence_sha256": digest(path.read_bytes()),
        "total": 180,
        "changed": sum(r["changed"] for r in summary["cases"]),
        "by_arm": computed,
        "scope": inventory["scope"],
    }


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--capture", type=Path, help="Completed local collection to package once")
    parser.add_argument("--evidence", type=Path, default=config.ROOT / DESTINATION)
    args = parser.parse_args()
    if args.capture:
        capture(args.capture.resolve(), args.evidence)
    result = verify(args.evidence)
    (args.evidence / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
