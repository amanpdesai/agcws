"""Publish exact selected reference evidence; never run experiments.

Usage: python -m agcws.reporting.reference_repair {publish,verify} --root .
Native power JSON is copied without serialization. Historical absolute paths in
bank records are provenance labels; qualification evidence is embedded locally.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from agcws.reporting.metrics import key
from agcws.reporting.reference_audit import digest, maximum_error, validity

DESIGNS = ("aes", "dma", "ibex", "mesh", "redmule")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def put(path, data):
    """Idempotent publication, refusing to overwrite different evidence."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data, f"Existing evidence differs: {path}"
    else:
        with path.open("xb") as stream:
            stream.write(data)


def check_join(case, measurement):
    activity = measurement["activity"]
    for field in ("program", "rates", "target_rates", "scale", "max_bin_error"):
        assert activity[field] == case[field], (case["target"], field)
    assert activity["target"] == case["target"]
    assert activity["activity_solved"] is True


def power_sources(root, design):
    if design == "dma":
        archive = root / "results/dma/power/measurements.jsonl.gz"
        with gzip.open(archive, "rt") as stream:
            for line in stream:
                bucket = json.loads(line)
                if bucket["bucket"] != "references-dma":
                    continue
                for row in bucket["records"]:
                    raw = row["raw_measurement"].encode()
                    assert sha(raw) == row["receipt"]["measurement_sha256"]
                    m = json.loads(raw)
                    assert m["activity"] == row["case"]
                    yield m, raw, {"reused": True, "archive": str(archive.relative_to(root)),
                                   "archive_sha256": sha(archive.read_bytes()), "receipt": row["receipt"]}, None
    else:
        base = root / "out/reference-repair-v1/power-preparation-v2" / design
        plan = json.loads((base / "plan.json").read_bytes())
        for path in sorted(base.glob("*/measurement.json")):
            raw = path.read_bytes()
            receipt = json.loads((path.parent / "complete.json").read_bytes())
            assert sha(raw) == receipt["measurement_sha256"]
            m = json.loads(raw)
            assert m["plan_sha256"] == plan["sha256"]
            assert m["activity"] in plan["cases"]
            yield m, raw, {"reused": False, "source": str(path.relative_to(root)),
                           "receipt": receipt}, path.parent


def publish(root):
    bank_path = root / "out/reference-repair-v1/reference-bank-v1.json"
    bank = json.loads(bank_path.read_bytes())
    for design in DESIGNS:
        cases = {c["target"]: c for c in bank["cases"] if c["design"] == design}
        index = {"version": "repaired-references-v1", "references": {}, "provenance": {}}
        power_dir = root / "results" / design / "power/repaired-references-v1"
        for m, raw, provenance, source_dir in power_sources(root, design):
            target = m["activity"]["target"]
            if target not in cases:
                continue
            assert target not in index["references"], target
            check_join(cases[target], m)
            path = power_dir / target / "measurement.json"
            put(path, raw)
            index["references"][target] = {"path": str(path.relative_to(root)), "sha256": sha(raw)}
            index["provenance"][target] = provenance
        assert len(index["references"]) == len(cases) == 8
        put(power_dir / "index.json", encoded(index))
        print(f"Published {design}: {power_dir / 'index.json'}", flush=True)


def package(root):
    bank = json.loads((root / "out/reference-repair-v1/reference-bank-v1.json").read_bytes())
    for design in DESIGNS:
        cases = [c for c in bank["cases"] if c["design"] == design]
        base = root / "results" / design
        task_dir = base / "tasks/repaired-references-v1"
        power_dir = base / "power/repaired-references-v1"
        evidence = {}

        def add(name, raw):
            evidence[name] = {"sha256": sha(raw), "text": raw.decode()}

        for c in cases:
            prefix = c["target"] + "/"
            source = c["source"]
            if source["kind"] == "fresh-independent-reference":
                for name in ("request", "measurement", "qualification"):
                    raw = Path(source[name]).read_bytes()
                    assert sha(raw) == source[name + "_sha256"]
                    add(prefix + name + ".json", raw)
            else:
                raw = Path(source["bundle"]).read_bytes()
                assert sha(raw) == source["bundle_sha256"]
                archive = json.loads(gzip.decompress(raw))
                member = archive[source["member"]]["text"].encode()
                assert sha(member) == source["member_sha256"]
                row = json.loads(member)["results"][source["record_index"]]
                assert digest(row) == source["record_sha256"]
                add(prefix + "original-record.json", encoded(row))
                add(prefix + "measurement.json", encoded(row["measurement"]))
            for n, f in enumerate(c["functional_sources"]):
                raw = Path(f["path"]).read_bytes()
                assert sha(raw) == f["sha256"]
                add(prefix + f"functional-{n}.json", raw)
        add("frozen-task.json", (base / "tasks/plan/config.json").read_bytes())
        # Preserve construction and selection recipes, not simulation binaries/waves.
        recipes = [root / "out/reference-repair-v1/build_reference_bank.py",
                   root / "out/reference-repair-v1/verify_reference_bank.py"]
        recipes += list((root / "out/reference-repair-v1").glob(f"repair_{design}.py"))
        for folder in (root / "out/reference-repair-v1").glob(design + "-*"):
            if folder.is_dir():
                recipes += list(folder.glob("*.py")) + list(folder.glob("*.md"))
        for path in sorted(set(recipes)):
            add("recipes/" + str(path.relative_to(root / "out/reference-repair-v1")), path.read_bytes())
        put(task_dir / "bank.json", encoded({"version": "repaired-references-v1", "cases": cases,
            "selection": bank["selection"], "selection_uses_power": False,
            "historical_paths": "Provenance labels only; use evidence.json.gz for qualification replay."}))
        put(task_dir / "evidence.json.gz", gzip.compress(encoded(evidence), mtime=0))

        proof = {}
        for m, raw, provenance, source_dir in power_sources(root, design):
            if m["activity"]["target"] not in {c["target"] for c in cases}:
                continue
            target = m["activity"]["target"]
            files = {}
            if source_dir is not None:
                names = ["request.json", "complete.json", "rtl/replay-request.json",
                         "rtl/replay-receipt.json", "rtl/replay-result.json",
                         "gls/functional.json", "gls/receipt.json", "gls/power_clock.json"]
                names += ["power/" + n for n in m["power"]["artifact_sha256"]]
                for name in names:
                    path = source_dir / name
                    if not path.exists():
                        continue
                    data = path.read_bytes()
                    if name.startswith("power/"):
                        assert sha(data) == m["power"]["artifact_sha256"][path.name]
                    excerpt = path.suffix == ".rpt" and len(data) > 1000000
                    text = data.decode()
                    if excerpt:
                        text = "\n".join(line for line in text.splitlines() if
                            line.startswith(("Total ", "vcd ", "unannotated ", "LEAF_SWITCHING_SUM "))) + "\n"
                    files[name] = {"source_sha256": sha(data), "sha256": sha(text.encode()),
                                   "summary_excerpt_only": excerpt, "text": text}
                for name, expected in m["power"]["inputs"].items():
                    if Path(name).name == "manifest.json":
                        data = Path(name).read_bytes()
                        assert sha(data) == expected
                        files["synthesis-manifest.json"] = {"sha256": sha(data), "text": data.decode()}
            proof[target] = {"provenance": provenance, "files": files,
                             "measurement_sha256": sha(raw)}
        put(power_dir / "evidence.json.gz", gzip.compress(encoded(proof), mtime=0))
        index_path = power_dir / "index.json"
        index = json.loads(index_path.read_bytes())
        dependencies = [task_dir / "bank.json", task_dir / "evidence.json.gz", power_dir / "evidence.json.gz"]
        dependencies += list(task_dir.glob("*.md"))
        index["inputs"] = {str(p.relative_to(root)): sha(p.read_bytes()) for p in dependencies}
        # This index was generated by publish(); only augment its dependency map.
        index_path.write_bytes(encoded(index))


def verify(root):
    count = 0
    for design in DESIGNS:
        base = root / "results" / design
        index = json.loads((base / "power/repaired-references-v1/index.json").read_bytes())
        assert len(index["references"]) == 8
        for path, expected in index.get("inputs", {}).items():
            assert sha((root / path).read_bytes()) == expected, path
        task_dir = base / "tasks/repaired-references-v1"
        cases = {}
        if task_dir.exists():
            cases = {c["target"]: c for c in json.loads((task_dir / "bank.json").read_bytes())["cases"]}
            evidence = json.loads(gzip.decompress((task_dir / "evidence.json.gz").read_bytes()))
            for entry in evidence.values():
                assert sha(entry["text"].encode()) == entry["sha256"]
            task = json.loads(evidence["frozen-task.json"]["text"])
            for target, c in cases.items():
                m = json.loads(evidence[target + "/measurement.json"]["text"])
                assert digest(c["program"]) == c["program_sha256"]
                assert digest(c["measurement_manifest"]) == c["manifest_sha256"]
                assert m["cache_id"] == key({"program": c["program"], "measurement": c["measurement_manifest"]["measurement_fingerprint"]})
                assert validity(design, c["program"], m) == []
                assert m["profile"]["window_rates"] == c["rates"]
                assert c["target_rates"] == task["targets"][target] and c["scale"] == task["scale"]
                assert maximum_error(c["rates"], c["target_rates"], c["scale"]) == c["max_bin_error"] <= task["tolerance"] == .05
                for n, source in enumerate(c["functional_sources"]):
                    assert evidence[target + f"/functional-{n}.json"]["sha256"] == source["sha256"]
                if c["source"]["kind"] == "fresh-independent-reference":
                    for name in ("request", "measurement", "qualification"):
                        assert evidence[target + "/" + name + ".json"]["sha256"] == c["source"][name + "_sha256"]
                    request = json.loads(evidence[target + "/request.json"]["text"])
                    assert request["program"] == c["program"] and request["manifest"] == c["measurement_manifest"]
                else:
                    row = json.loads(evidence[target + "/original-record.json"]["text"])
                    assert digest(row) == c["source"]["record_sha256"]
                    assert row["program"] == c["program"] and row["measurement"] == m
            proof = json.loads(gzip.decompress((base / "power/repaired-references-v1/evidence.json.gz").read_bytes()))
            assert set(proof) == set(cases) == set(index["references"])
            for target, item in proof.items():
                assert item["measurement_sha256"] == index["references"][target]["sha256"]
                native = json.loads((root / index["references"][target]["path"]).read_bytes())
                for name, entry in item["files"].items():
                    assert sha(entry["text"].encode()) == entry["sha256"]
                    if name.startswith("power/"):
                        assert entry["source_sha256"] == native["power"]["artifact_sha256"][name.split("/")[-1]]
        for target, entry in index["references"].items():
            raw = (root / entry["path"]).read_bytes()
            assert sha(raw) == entry["sha256"]
            assert json.loads(raw)["activity"]["target"] == target
            if cases:
                check_join(cases[target], json.loads(raw))
            count += 1
    return {"verified_native_measurements": count}


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("command", choices=("publish", "package", "verify"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "publish":
        publish(root)
    elif args.command == "package":
        package(root)
    print(json.dumps(verify(root), sort_keys=True))


if __name__ == "__main__":
    main()
