#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
source scripts/load_env.sh
out_dir=${1:-out/axi-dma-synthesis}
liberty=${2:-${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}}
yosys_bin=${AGCWS_YOSYS:-yosys}
mkdir -p "$out_dir"

sources=(third_party/verilog-axi/rtl/axi_dma.v
         third_party/verilog-axi/rtl/axi_dma_rd.v
         third_party/verilog-axi/rtl/axi_dma_wr.v)
"$yosys_bin" -Q -T -p "read_verilog -lib ${sources[*]}; read_verilog ${sources[*]}; \
  hierarchy -top axi_dma; proc; opt; memory_map; opt; flatten; opt; techmap; opt; \
  dfflibmap -liberty $liberty; abc -liberty $liberty; clean; \
  write_verilog -noattr -noexpr $out_dir/mapped.v; \
  tee -o $out_dir/stat.json stat -liberty $liberty -json" \
  > "$out_dir/yosys.log" 2>&1

sha256sum "$out_dir/mapped.v" | awk '{print $1}' > "$out_dir/netlist.sha256"
sha256sum "$liberty" | awk '{print $1}' > "$out_dir/liberty.sha256"
python3 - "$out_dir/manifest.json" "$liberty" "$out_dir" "$yosys_bin" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

manifest, liberty, out_dir, yosys = sys.argv[1:]
root = Path(out_dir)
Path(manifest).write_text(json.dumps({
    "top": "axi_dma",
    "liberty": liberty,
    "netlist_sha256": (root / "netlist.sha256").read_text().strip(),
    "liberty_sha256": (root / "liberty.sha256").read_text().strip(),
    "yosys_version": subprocess.run([yosys, "-V"], capture_output=True,
                                     text=True, check=True).stdout.strip(),
}, indent=2) + "\n")
PY
echo "AXI_DMA_SYNTHESIS_DONE out=$out_dir"
