"""Verify compact evidence hashes without restoring or executing a study."""

import argparse
import json
from pathlib import Path


def main(argv=None):
    from agcws.evidence.packs import verify

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, required=True)
    args = parser.parse_args(argv)
    result = verify(args.study.resolve(strict=True))
    print(json.dumps(result, indent=2))
    return result
