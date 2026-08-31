#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
out_dir=${1:-"$repo_root/out/axi-dma-rd-smoke"}
if [[ $# -gt 0 ]]; then shift; fi
mkdir -p "$out_dir"

iverilog_bin=${AGCWS_IVERILOG:-iverilog}
"$iverilog_bin" -g2012 -s agcws_axi_dma_rd_smoke -o "$out_dir/smoke.vvp" \
  "$repo_root/third_party/harnesses/axi_dma_rd_smoke.v" \
  "$repo_root/third_party/verilog-axi/rtl/axi_dma_rd.v"
(cd "$out_dir" && vvp smoke.vvp "$@")

test -s "$out_dir/activity.vcd"
printf 'axi_dma_rd smoke OK: %s\n' "$out_dir/activity.vcd"
