#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
if [[ $# -ne 2 ]]; then
  echo "usage: $0 WORKLOAD.json OUTPUT_DIR" >&2
  exit 2
fi
workload=$1
out_dir=$2
mkdir -p "$out_dir"
python_bin=${AGCWS_PYTHON:-python3}
export AGCWS_DMA_WORKLOAD=$(realpath "$workload")
fst2vcd_bin=${AGCWS_FST2VCD:-fst2vcd}

PYTHONPATH="$repo_root/third_party/harnesses${PYTHONPATH:+:$PYTHONPATH}" \
  "$python_bin" - "$repo_root" "$out_dir" <<'PY'
import os
import sys
from pathlib import Path
from cocotb_test.simulator import run

repo, out = map(Path, sys.argv[1:])
run(verilog_sources=[
    repo / "third_party/verilog-axi/rtl/axi_dma.v",
    repo / "third_party/verilog-axi/rtl/axi_dma_rd.v",
    repo / "third_party/verilog-axi/rtl/axi_dma_wr.v",
], toplevel="axi_dma", module="axi_dma_coupled_tb", simulator="icarus",
   sim_build=str(out / "sim_build"), waves=True)
PY
fst=$(find "$out_dir/sim_build" -maxdepth 1 -name '*.fst' -print -quit)
if [[ -z "$fst" ]]; then
  echo "coupled harness did not produce an FST waveform" >&2
  exit 1
fi
"$fst2vcd_bin" "$fst" > "$out_dir/activity.vcd"
PYTHONPATH="$repo_root/src" "$python_bin" "$repo_root/scripts/parse_vcd_activity.py" \
  "$out_dir/activity.vcd" --clock clk --output "$out_dir/activity.json"
"$python_bin" - "$workload" "$out_dir" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

workload, out = map(Path, sys.argv[1:])

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

payload = json.loads(workload.read_text())
manifest = {
    "backend": "cocotb_axi_ram_coupled",
    "coupled_axi_dma_top": True,
    "workload_sha256": sha256(workload),
    "waveform": "activity.vcd",
    "waveform_sha256": sha256(out / "activity.vcd"),
    "activity": "activity.json",
    "activity_sha256": sha256(out / "activity.json"),
    "transfers": len(payload["transfers"]),
    "useful_work_bytes": sum(int(t["length"]) for t in payload["transfers"]),
}
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
PY
echo "AGCWS_AXI_DMA_COUPLED_DONE out=$out_dir"
