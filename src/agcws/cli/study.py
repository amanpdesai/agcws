"""Commands for preparing, running, inspecting and exporting studies."""

import argparse
import json
from pathlib import Path

from agcws.core.config import ROOT
from agcws.studies import engine


def main(argv=None):
    parser = argparse.ArgumentParser(description="AGCWS study pipeline (no implicit execution)")
    sub = parser.add_subparsers(dest="action", required=True)
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
    if args.action == "prepare":
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
