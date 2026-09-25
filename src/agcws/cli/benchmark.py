"""Assess recorded request/witness pairs; this command never searches or changes targets."""

import argparse
import json
from pathlib import Path


def main(argv=None):
    from agcws.studies.targets import qualify

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="JSON: scale, tolerance, nonflat_margin, pairs[{request,witness}]")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    data = json.loads(args.input.read_text())
    result = [{"request": pair["request"], **qualify(pair["request"], pair["witness"],
              scale=data["scale"], tolerance=data["tolerance"], nonflat_margin=data["nonflat_margin"])}
              for pair in data["pairs"]]
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"requests": len(result), "qualified": sum(r["qualified"] for r in result)}))
    return result
