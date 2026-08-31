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
out_dir=${2:-out/aes-cross-pdk}
sky_lib=${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}
nangate_lib=${AGCWS_LIBERTY_NANGATE45:-third_party/liberty/nangate45/Nangate45_typ.lib}
mkdir -p "$out_dir"

for name in sky130hd nangate45; do
  if [[ "$name" == sky130hd ]]; then lib=$sky_lib; else lib=$nangate_lib; fi
  AGCWS_LIBERTY="$lib" AGCWS_SLANG_PLUGIN="${AGCWS_SLANG_PLUGIN:-}" \
    bash scripts/synthesize_aes_core.sh "$out_dir/$name-synthesis"
  bash scripts/run_opensta_aes.sh "$out_dir/$name-synthesis" "$waveform" \
    "$out_dir/$name-power" "$lib"
done

python3 - "$out_dir/comparison.json" "$out_dir" "$waveform" "$sky_lib" "$nangate_lib" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

output, root, waveform, sky_lib, nangate_lib = sys.argv[1:]
def power(name):
    for line in (Path(root) / f"{name}-power/power.rpt").read_text().splitlines():
        fields = line.split()
        if fields and fields[0] == "Total" and len(fields) >= 5:
            return float(fields[4])
    raise ValueError(f"no total power in {name} report")
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

Path(output).write_text(json.dumps({
    "waveform": str(Path(waveform).resolve()),
    "pdks": {
        "sky130hd": {"liberty": sky_lib, "liberty_sha256": sha(sky_lib), "total_power_w": power("sky130hd")},
        "nangate45": {"liberty": nangate_lib, "liberty_sha256": sha(nangate_lib), "total_power_w": power("nangate45")},
    },
}, indent=2) + "\n")
PY
echo "CROSS_PDK_DONE comparison=$out_dir/comparison.json"
