#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
source scripts/load_env.sh
out_dir=${1:-out/axi-dma-synthesis}
liberty=${2:-${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}}
yosys_bin=${AGCWS_YOSYS:-yosys}
memory_libmap=${AGCWS_MEMORY_LIBMAP:-}
memory_manifest=${AGCWS_MEMORY_MANIFEST:-}
mkdir -p "$out_dir"

memory_pass="memory_map"
if [[ -n "$memory_libmap" ]]; then
  test -f "$memory_libmap" || { echo "missing AGCWS_MEMORY_LIBMAP: $memory_libmap" >&2; exit 2; }
  test -f "$memory_manifest" || { echo "set AGCWS_MEMORY_MANIFEST" >&2; exit 2; }
  python3 - "$memory_manifest" <<'PY'
import json
import sys
manifest = json.load(open(sys.argv[1], encoding="utf-8"))
if manifest.get("mapping_policy") != "map_eligible_flatten_incompatible":
    raise SystemExit("memory collateral lacks the mixed mapping/flatten policy")
PY
  echo "mapping eligible memories; incompatible memories will remain flop-mapped" >&2
  memory_pass="memory_libmap -lib $memory_libmap; memory_map"
fi

sources=(third_party/verilog-axi/rtl/axi_dma.v
         third_party/verilog-axi/rtl/axi_dma_rd.v
         third_party/verilog-axi/rtl/axi_dma_wr.v)
"$yosys_bin" -Q -T -p "read_verilog -lib ${sources[*]}; read_verilog ${sources[*]}; \
  hierarchy -top axi_dma; proc; opt; $memory_pass; opt; flatten; opt; techmap; opt; \
  dfflibmap -liberty $liberty; abc -liberty $liberty; clean; \
  write_verilog -noattr -noexpr $out_dir/mapped.v; \
  tee -o $out_dir/stat.json stat -liberty $liberty -json" \
  > "$out_dir/yosys.log" 2>&1

sha256sum "$out_dir/mapped.v" | awk '{print $1}' > "$out_dir/netlist.sha256"
sha256sum "$liberty" | awk '{print $1}' > "$out_dir/liberty.sha256"
python3 - "$out_dir/manifest.json" "$liberty" "$out_dir" "$yosys_bin" "$memory_libmap" "$memory_manifest" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

manifest, liberty, out_dir, yosys, memory_libmap, memory_manifest = sys.argv[1:]
root = Path(out_dir)
memory_sha256 = None
memory_manifest_sha256 = None
if memory_libmap:
    import hashlib
    memory_sha256 = hashlib.sha256(Path(memory_libmap).read_bytes()).hexdigest()
    memory_manifest_sha256 = hashlib.sha256(Path(memory_manifest).read_bytes()).hexdigest()
Path(manifest).write_text(json.dumps({
    "top": "axi_dma",
    "liberty": liberty,
    "netlist_sha256": (root / "netlist.sha256").read_text().strip(),
    "liberty_sha256": (root / "liberty.sha256").read_text().strip(),
    "yosys_version": subprocess.run([yosys, "-V"], capture_output=True,
                                     text=True, check=True).stdout.strip(),
    "memory_libmap": memory_libmap or None,
    "memory_libmap_sha256": memory_sha256,
    "memory_manifest": memory_manifest or None,
    "memory_manifest_sha256": memory_manifest_sha256,
}, indent=2) + "\n")
PY
echo "AXI_DMA_SYNTHESIS_DONE out=$out_dir"
