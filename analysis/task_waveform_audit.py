"""Recount preselected burst/control witnesses without simulation or model calls."""

import argparse
import concurrent.futures
import json
from pathlib import Path

from activity_recount import recount

CONTRACTS = {
    "aes": ("aes_core_smoke.dut", "aes_core_smoke.clk_i"),
    "dma": ("axi_dma", "axi_dma.clk"),
    "mesh": ("mesh_temporal.dut", "mesh_temporal.clk"),
    "redmule": ("redmule_tb_wrap.i_redmule_tb.i_redmule_wrap", "redmule_tb_wrap.clk"),
}


def check(case):
    design, family, path, expected = case
    result = recount(path, *CONTRACTS[design])
    if [r[0] for r in result["bin_rates"]] != expected:
        raise ValueError(f"event rates fail to reproduce: {design}/{family}")
    return {"design": design, "family": family, "waveform": str(path), **result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = []
    for design in CONTRACTS:
        bank = json.loads(Path(f"results/{design}/qualified-bank-v6.json").read_text())
        root = Path(f"out/{design}-runtime-replay-v5/replay/cache")
        for request in bank["splits"]["confirmation"]["requests"]:
            if request["id"] not in ("burst", "flat_control"):
                continue
            cache = root / request["witness_cache_id"]
            measured = json.loads((cache / "result.json").read_text())
            paths = list(cache.glob("attempt-*/activity.vcd"))
            if len(paths) != 1:
                raise ValueError(f"ambiguous or missing waveform: {cache}")
            cases.append((design, request["id"], paths[0], measured["profile"]["window_rates"]))
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        records = list(executor.map(check, cases))
    report = {"selection": "confirmation burst and flat control, all four identifier-event designs",
              "scope": "saved waveform recount, not new simulation; Ibex has a separate bit-counter contract",
              "llm_calls": 0, "simulation_calls": 0, "records": records}
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
