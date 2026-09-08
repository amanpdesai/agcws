"""Revision 2 changes only the native serving schema, retaining Stage A evidence."""

import argparse
import json
import subprocess
from pathlib import Path

from agcws.provenance import file_sha256
from experiments.ibex_temporal_v4 import contract_study as first
from experiments.ibex_temporal_v4.evaluate import write
from experiments.ibex_temporal_v4.native_schema import serving_schema


def freeze(root):
    first.freeze(root)
    manifest = json.loads((root / "manifest.json").read_text())
    protocol = Path("docs/IBEX_CONTRACT_V4_REVISION2.md")
    committed = subprocess.check_output(["git", "show", f"HEAD:{protocol}"])
    if first.digest(committed) != file_sha256(protocol):
        raise ValueError("commit revision protocol before freeze")
    manifest["sources"][str(protocol)] = file_sha256(protocol)
    manifest["revision"] = "native-serving-schema-v2"
    manifest["prior_manifest_sha256"] = file_sha256(
        Path("results/ibex_temporal_v4_contract/manifest.json")
    )
    write(root / "schema.json", serving_schema(2))
    manifest["schema_sha256"] = file_sha256(root / "schema.json")
    write(root / "manifest.json", manifest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("freeze", "run", "summarize"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.root)
    elif args.action == "run":
        first.run(args.root)
    else:
        print(json.dumps(first.summarize(args.root), indent=2))
