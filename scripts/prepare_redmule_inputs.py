"""Emit checked timed GEMM stimulus headers without numerical-library dependencies."""

import argparse
import json
from pathlib import Path

from agcws.adapters.redmule import stimulus_headers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workload", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    headers = stimulus_headers(json.loads(args.workload.read_text()))
    args.out.mkdir(parents=True, exist_ok=False)
    for name, text in headers.items():
        (args.out / name).write_text(text)


if __name__ == "__main__":
    main()
