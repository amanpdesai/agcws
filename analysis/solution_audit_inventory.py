"""Seal or verify the offline solution audit's compact evidence and dependencies."""

import argparse
import hashlib
import json
import shutil
import tarfile
from pathlib import Path

from analysis.solution_audit import digest, read


def inventory():
    root = Path("results/solution_audit_v1")
    paths = set(root.rglob("*.json")) - {root / "inventory.json"}
    paths.update(Path("analysis").glob("solution*.py"))
    paths.update(Path("src/agcws/pipeline/ibex").glob("*.py"))
    paths.update([Path("tests/test_solution_audit.py"), Path("docs/SOLUTION_AUDIT.md")])
    paths.update(Path("results/nonflat_temporal_v1").glob("*.json"))
    original = [
        "experiments/baseline_panel_v1/policies.py",
        "experiments/temporal_scaling_v1/baselines.py",
        "experiments/nonflat_temporal_v1/study.py",
    ]
    with tarfile.open("archive/legacy-source.tar.gz") as archive:
        sources = {
            name: hashlib.sha256(archive.extractfile(name).read()).hexdigest() for name in original
        }
    converter = shutil.which("fst2vcd")
    if not converter:
        raise ValueError("fst2vcd unavailable for inventory")
    return {
        "files_sha256": {str(p): digest(p) for p in sorted(paths)},
        "original_sources_sha256": sources,
        "archive_sha256": digest(Path("archive/legacy-source.tar.gz")),
        "converter_sha256": digest(Path(converter)),
        "selection_commit": "7e43ae8d4",
        "protocol_commit": "fa43ac439",
        "run_note": "Offline only. Trace script was subsequently hardened for subprocess cleanup and reads scale from the frozen manifest instead of the identical literal 528.45376. Counter and rebin semantics unchanged.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    path = Path("results/solution_audit_v1/inventory.json")
    result = inventory()
    if args.verify:
        if result != read(path):
            raise ValueError("audit inventory differs")
        print("Audit inventory verified")
    else:
        with path.open("x") as output:
            json.dump(result, output, indent=2)
            output.write("\n")


if __name__ == "__main__":
    main()
