"""Independent recount of the preselected burst/control schedule witnesses."""

import argparse
import concurrent.futures
import json
from pathlib import Path

from activity_recount import recount


def verify(case):
    design, family, root = case
    row = json.loads((root / "replay/panel" / f"confirmation-{family}" / "result.json").read_text())
    result = row["measurement"]
    if result["valid"] is not True:
        return {"design": design, "family": family, "valid": False, "stage": result["stage"]}
    profile = result["profile"]
    paths = list((root / "replay/cache" / result["cache_id"]).glob("attempt-*/activity.vcd"))
    if len(paths) != 1:
        raise ValueError("missing or ambiguous witness waveform")
    reference = recount(paths[0], profile["scope"], profile["clock"], exclude_clock=True)
    rates = [v[1] for v in reference["bin_rates"]]
    if rates != profile["window_rates"] or reference["clock_edges"] != profile["clock_edges"]:
        raise ValueError(f"independent bit recount differs: {design}/{family}")
    return {"design": design, "family": family, "valid": True, "exact_bit_rate_match": True,
            "native_contract": profile["activity_contract"], "cache_id": result["cache_id"],
            "reference": reference}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = [(d, family, args.root / d) for d in ("aes", "dma", "mesh", "redmule")
             for family in ("burst", "flat_control")]
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as pool:
        records = list(pool.map(verify, cases))
    with args.output.open("x") as stream:
        json.dump({"scope": "independent schedule witness recount, not new simulation or Ibex verification",
                   "records": records}, stream, indent=2)
        stream.write("\n")
