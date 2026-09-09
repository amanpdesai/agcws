"""Filter a waveform deletion plan to retain each completed cell's best candidate."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from maintenance.clean_artifacts import REPO, checked_file


def protected_ids(archive):
    index = json.loads((archive / "sha256.json").read_text())

    def read(name):
        data = (archive / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != index[name]:
            raise ValueError(f"archive evidence changed: {name}")
        return json.loads(gzip.decompress(data) if name.endswith(".gz") else data)

    manifest = read("manifest.json")
    if read("aggregate.json")["complete_study"] is not True:
        raise ValueError("depth panel is not complete")
    selected = set()
    for cell in manifest["cells"]:
        directory = f"panel/{cell['target']}/{cell['seed']}/{cell['arm']}"
        trials = [
            t
            for slot in range(1, 129, 2)
            for t in read(f"{directory}/batches/{slot:03}/trials.json.gz")
        ]
        if [t["slot"] for t in trials] != list(range(1, 129)):
            raise ValueError("incomplete cell")
        valid = [t for t in trials if t["valid"]]
        if not valid:
            raise ValueError("no finalist; manually review this cell")
        selected.add(min(valid, key=lambda t: (t["loss"], t["slot"]))["cache_id"])
    return selected


def filter_plan(plan_path, archive, output):
    plan = json.loads(plan_path.read_text())
    if plan["root"] != str(REPO / "out") or plan["targets"] != ["ibex-depth-v1"]:
        raise ValueError("only the explicit completed depth run is supported")
    keep = protected_ids(archive)
    selected, retained = [], []
    for entry in plan["files"]:
        checked_file(REPO / "out", entry, plan["targets"])
        parts = Path(entry["path"]).parts
        if len(parts) < 4 or parts[:2] != ("ibex-depth-v1", "cache"):
            raise ValueError("unexpected waveform outside candidate cache")
        (retained if parts[2] in keep else selected).append(entry)
    result = {
        **plan,
        "files": selected,
        "allocated_bytes": sum(
            (REPO / "out" / e["path"]).stat().st_blocks * 512 for e in selected
        ),
        "protected_cache_ids": sorted(keep),
        "retained_finalist_files": len(retained),
        "archive_index_sha256": hashlib.sha256(
            (archive / "sha256.json").read_bytes()
        ).hexdigest(),
    }
    with output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(
        json.dumps(
            {
                "planned_nonfinalist_files": len(selected),
                "retained_finalist_files": len(retained),
                "allocated_bytes": result["allocated_bytes"],
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    filter_plan(args.plan, args.archive, args.out)
