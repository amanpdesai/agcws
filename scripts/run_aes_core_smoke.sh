#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
out_dir=${1:-out/aes-core-smoke}
mkdir -p "$out_dir"
python3 scripts/resolve_sv_sources.py --top aes_cipher_core > "$out_dir/sources.list"
verilator --binary --trace-vcd --timing --sv --top-module aes_core_smoke \
  -Wno-fatal -Wno-WIDTHTRUNC \
  -Mdir "$out_dir/obj_dir" -o aes_core_smoke \
  -Ithird_party/opentitan/hw/ip/aes/rtl \
  -Ithird_party/opentitan/hw/ip/prim/rtl \
  -Ithird_party/opentitan/hw/ip/prim_generic/rtl \
  -Ithird_party/opentitan/hw/ip/edn/rtl \
  -Ithird_party/opentitan/hw/ip/csrng/rtl \
  -Ithird_party/opentitan/hw/ip/entropy_src/rtl \
  $(<"$out_dir/sources.list") experiments/aes_core_smoke.sv
"$out_dir/obj_dir/aes_core_smoke" > "$out_dir/run.log"
mv activity.vcd "$out_dir/activity.vcd"
python3 scripts/parse_vcd_activity.py "$out_dir/activity.vcd" \
  --windows 8 --output "$out_dir/activity.json"
