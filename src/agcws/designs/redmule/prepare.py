"""Derive a timed testbench without modifying RedMulE or its pinned checkout."""

import argparse
import hashlib
import json
from pathlib import Path

from agcws.core.config import ROOT as _REPO_ROOT


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"upstream harness changed at anchor: {old[:70]}")
    return text.replace(old, new, 1)


def timed_testbench(original):
    text = replace_once(original, "  logic other_r_valid;", """  logic other_r_valid;
  int unsigned observation_cycles = 65536;
  int unsigned observed_cycles = 0;
  logic [31:0] timer_read_data = 0;
  bit reference_done = 0;
  always @(posedge clk_i) begin
    observed_cycles <= observed_cycles + 1;
    if (data_req && data_addr == 32'h80000008)
      timer_read_data <= observed_cycles;
    else timer_read_data <= 0;
  end
  initial begin
    if (!$value$plusargs("OBSERVATION_CYCLES=%d", observation_cycles))
      observation_cycles = 65536;
    if (observation_cycles < 8192) $fatal(1, "observation window too short");
    repeat (observation_cycles) @(posedge clk_i);
    #1;
    if (!reference_done) $fatal(1, "REDMULE_INCOMPLETE fixed observation ended before reference check");
    $display("AGCWS_REDMULE_WINDOW_DONE cycles=%0d", observed_cycles);
    $finish;
  end""")
    text = replace_once(text, "tcdm[MP].r_valid ? tcdm[MP].r_data : '0;",
                        "tcdm[MP].r_valid ? tcdm[MP].r_data : timer_read_data;")
    text = replace_once(text, "    $finish;\n  end\n\nendmodule // redmule_tb",
                        "    reference_done = 1;\n  end\n\nendmodule // redmule_tb")
    return text


def timed_wrapper(original):
    start = original.index("  // Performs one entire clock cycle.")
    return original[:start] + """  initial begin
    clk = 0;
    forever #(TCP/2) clk = ~clk;
  end
  initial begin
    $dumpfile("activity.fst");
    $dumpvars(0, redmule_tb_wrap);
    rst_n = 0;
    fetch_enable = 0;
    repeat (20) @(negedge clk);
    rst_n = 1;
    repeat (10) @(negedge clk);
    rst_n = 0;
    repeat (10) @(negedge clk);
    rst_n = 1;
    repeat (100) @(negedge clk);
    fetch_enable = 1;
  end
endmodule
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-list", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    repo = _REPO_ROOT
    upstream = repo / "benchmarks/redmule/target/sim/src"
    args.out.mkdir(parents=True, exist_ok=False)
    sources = args.source_list.read_text()
    hashes = {}
    for name, transform in (("redmule_tb.sv", timed_testbench), ("redmule_tb_wrap.sv", timed_wrapper)):
        source = upstream / name
        original = source.read_text()
        generated = "// AGCWS derived timing harness; original license and attribution below.\n" + transform(original)
        output = args.out / name
        output.write_text(generated)
        matches = [line for line in sources.splitlines() if line.endswith("/" + name)]
        if len(matches) != 1:
            raise ValueError(f"exactly one {name} source entry required")
        container_path = "/workspace/" + str(output.resolve().relative_to(repo))
        sources = replace_once(sources, matches[0], container_path)
        hashes[name] = {"upstream_sha256": hashlib.sha256(original.encode()).hexdigest(),
                        "generated_sha256": hashlib.sha256(generated.encode()).hexdigest()}
    (args.out / "sources.vlt").write_text(sources)
    (args.out / "derivation.json").write_text(json.dumps({"scope": "testbench only; no design RTL changes",
        "files": hashes, "timer_address": "0x80000008", "window": "continuous clock, including reset"}, indent=2) + "\n")


if __name__ == "__main__":
    main()
