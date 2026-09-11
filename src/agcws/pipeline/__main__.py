"""One explicit command surface; read-only operations never initialize a model."""

import argparse
import json
import sys
from pathlib import Path

from agcws.config import ROOT
from agcws.pipeline import archive, engine
from agcws.pipeline.spec import validate
from agcws.pipeline.storage import read


def main(argv=None):
    parser = argparse.ArgumentParser(description="AGCWS study pipeline (no implicit execution)")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("archive-check")
    sub.add_parser("archive-audit")
    extract = sub.add_parser("archive-extract")
    extract.add_argument("--destination", type=Path, required=True)
    check = sub.add_parser("validate")
    check.add_argument("--config", type=Path, required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--config", type=Path, required=True)
    prepare.add_argument("--directory", type=Path, required=True)
    run = sub.add_parser("run")
    run.add_argument("--directory", type=Path, required=True)
    run.add_argument("--execute", action="store_true")
    run.add_argument("--allow-paid", action="store_true")
    status = sub.add_parser("status")
    status.add_argument("--directory", type=Path, required=True)
    export = sub.add_parser("export")
    export.add_argument("--directory", type=Path, required=True)
    export.add_argument("--destination", type=Path, required=True)
    check_export = sub.add_parser("verify-export")
    check_export.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.action == "archive-check":
        m = archive.verify(ROOT)
        result = {
            "files": len(m["files"]),
            "commit": m["source_commit"],
            "verified": True,
        }
    elif args.action == "archive-extract":
        result = {"destination": str(archive.extract(ROOT, args.destination.resolve()))}
    elif args.action == "archive-audit":
        return archive.audit(ROOT, Path(sys.executable))
    elif args.action == "validate":
        result = {"valid": bool(validate(read(args.config)))}
    elif args.action == "prepare":
        result = engine.prepare(ROOT, args.config, args.directory.resolve())
    elif args.action == "run":
        if not args.execute:
            parser.error("run requires --execute; no work was launched")
        result = engine.run(ROOT, args.directory.resolve(), args.allow_paid)
    elif args.action == "status":
        result = engine.status(args.directory)
    elif args.action == "export":
        result = engine.export(args.directory, args.destination)
    elif args.action == "verify-export":
        result = engine.verify_export(args.directory)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
