#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
out_dir=${1:-"$repo_root/out/axi-dma-rtl"}
mkdir -p "$out_dir"

iverilog_bin=${AGCWS_IVERILOG:-iverilog}
"$iverilog_bin" -g2012 -s axi_dma -o "$out_dir/axi_dma.vvp" \
  "$repo_root/third_party/verilog-axi/rtl/axi_dma.v" \
  "$repo_root/third_party/verilog-axi/rtl/axi_dma_rd.v" \
  "$repo_root/third_party/verilog-axi/rtl/axi_dma_wr.v" \
  "$repo_root/third_party/verilog-axi/rtl/axi_dma_desc_mux.v"

printf 'axi_dma RTL compile OK: %s\n' "$out_dir/axi_dma.vvp"
