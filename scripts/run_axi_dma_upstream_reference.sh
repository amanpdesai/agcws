#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/agcws-verilog-axi.XXXXXX")
trap 'rm -rf "$tmp_dir"' EXIT

# The upstream testbench expects ../rtl relative to its working directory and
# loads MyHDL's VPI module by name. Keep both build products isolated from the
# pinned submodule and the project tree.
cp -a "$repo_root/third_party/verilog-axi" "$tmp_dir/verilog-axi"
(cd "$tmp_dir" && iverilog-vpi \
  -o myhdl.vpi \
  "$repo_root/.venv/share/myhdl/cosimulation/icarus/myhdl.c" \
  "$repo_root/.venv/share/myhdl/cosimulation/icarus/myhdl_table.c" \
  >/dev/null)

(cd "$tmp_dir/verilog-axi/tb" && \
  IVERILOG_VPI_MODULE_PATH="$tmp_dir" \
  PYTHONPATH="$tmp_dir/verilog-axi/tb" \
  "$repo_root/.venv/bin/python" test_axi_dma_32_32.py \
  > "$tmp_dir/upstream.log")

grep -q '^Running test' "$tmp_dir/upstream.log"
echo "AGCWS_AXI_DMA_UPSTREAM_REFERENCE_OK"
