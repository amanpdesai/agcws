#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
source scripts/load_env.sh
if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 WAVEFORM.vcd [OUTPUT_DIR]" >&2
  exit 2
fi
waveform=$1
out_dir=${2:-out/axi-dma-cross-pdk}
sky=${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}
nangate=${AGCWS_LIBERTY_NANGATE45:-third_party/liberty/nangate45/Nangate45_typ.lib}
mkdir -p "$out_dir"
for pdk in sky130hd nangate45; do
  lib=$sky
  [[ "$pdk" == nangate45 ]] && lib=$nangate
  bash scripts/synthesize_axi_dma.sh "$out_dir/$pdk-synthesis" "$lib"
  AGCWS_LIBERTY="$lib" bash scripts/run_opensta_axi_dma.sh \
    "$out_dir/$pdk-synthesis" "$waveform" "$out_dir/$pdk-power"
done
python3 - "$out_dir/comparison.json" "$out_dir" "$waveform" "$sky" "$nangate" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

output, root, waveform, sky, nangate = map(Path, sys.argv[1:])
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def record(name, lib):
    result = json.loads((root / f"{name}-power/result.json").read_text())
    return {"liberty": str(lib), "liberty_sha256": sha(lib),
            "total_power_w": result["mean_power"],
            "annotation": result["provenance"]}
output.write_text(json.dumps({
    "waveform": {"path": waveform.name, "sha256": sha(waveform)},
    "power_metric": "opensta_total_power_w",
    "pdks": {"sky130hd": record("sky130hd", sky),
             "nangate45": record("nangate45", nangate)},
}, indent=2) + "\n")
PY
echo "AXI_DMA_CROSS_PDK_DONE comparison=$out_dir/comparison.json"
