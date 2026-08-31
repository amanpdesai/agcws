#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/agcws-verilog-axi.XXXXXX")
trap 'rm -rf "$tmp_dir"' EXIT
output_dir=${1:-}
python_bin=${AGCWS_PYTHON:-.venv/bin/python}
if [[ "$python_bin" != /* ]]; then
  python_bin="$repo_root/$python_bin"
fi
iverilog_vpi_bin=$(command -v "${AGCWS_IVERILOG_VPI:-iverilog-vpi}")
myhdl_dir=$(realpath "${AGCWS_MYHDL_DIR:-${repo_root}/.venv/share/myhdl/cosimulation/icarus}")

# The upstream testbench expects ../rtl relative to its working directory and
# loads MyHDL's VPI module by name. Keep both build products isolated from the
# pinned submodule and the project tree.
cp -a "$repo_root/third_party/verilog-axi" "$tmp_dir/verilog-axi"
(cd "$tmp_dir" && "$iverilog_vpi_bin" \
  -o myhdl.vpi \
  "$myhdl_dir/myhdl.c" \
  "$myhdl_dir/myhdl_table.c" \
  >/dev/null)

(cd "$tmp_dir/verilog-axi/tb" && \
  IVERILOG_VPI_MODULE_PATH="$tmp_dir" \
  PYTHONPATH="$tmp_dir/verilog-axi/tb" \
  "$python_bin" test_axi_dma_32_32.py \
  > "$tmp_dir/upstream.log")

grep -q '^Running test' "$tmp_dir/upstream.log"
if [[ -n "$output_dir" ]]; then
  mkdir -p "$output_dir"
  cp "$tmp_dir/upstream.log" "$output_dir/upstream.log"
  "$python_bin" - "$output_dir/reference_manifest.json" "$repo_root" "$output_dir/upstream.log" <<'PY'
import hashlib
import json
import subprocess
import sys
from pathlib import Path

output, repo, log = map(Path, sys.argv[1:])
rtl = repo / "third_party/verilog-axi"
commit = subprocess.check_output(["git", "-C", str(rtl), "rev-parse", "HEAD"], text=True).strip()
digest = hashlib.sha256(log.read_bytes()).hexdigest()
output.write_text(json.dumps({
    "backend": "upstream_verilog_axi_myhdl_reference",
    "rtl_commit": commit,
    "log": {"path": log.name, "sha256": digest, "bytes": log.stat().st_size},
    "vpi_sources": [
        "myhdl.c",
        "myhdl_table.c",
    ],
    "assertion": "upstream coupled AXI DMA test completed successfully",
}, indent=2) + "\n")
PY
fi
echo "AGCWS_AXI_DMA_UPSTREAM_REFERENCE_OK"
