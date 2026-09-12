"""Seal and verify independent accounting audit code and compact records."""

import argparse
import json
from pathlib import Path

from analysis.accounting_audit import digest, read


def inventory():
    root = Path("results/accounting_audit_v1")
    paths = set(p for p in root.iterdir() if p.is_file() and p.name != "inventory.json")
    paths.update(Path("analysis").glob("accounting*.py"))
    paths.update([Path("tests/test_accounting_audit.py"), Path("docs/ACCOUNTING_AUDIT.md")])
    paths.update(Path("results/nonflat_temporal_v1").glob("*.json"))
    paths.update(Path("results/nonflat_temporal_v1").glob("evidence*.gz"))
    paths.add(Path("archive/legacy-source.tar.gz"))
    return {
        "checklist_commit": "cb4b6f351",
        "baseline_commit": "9917c492d",
        "sha256": {str(p): digest(p) for p in sorted(paths)},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    path = Path("results/accounting_audit_v1/inventory.json")
    result = inventory()
    if args.verify:
        if result != read(path):
            raise ValueError("accounting audit inventory differs")
        print("Accounting audit inventory verified")
    else:
        with path.open("x") as output:
            json.dump(result, output, indent=2)
            output.write("\n")


if __name__ == "__main__":
    main()
