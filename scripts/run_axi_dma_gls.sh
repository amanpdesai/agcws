#!/usr/bin/env bash
set -euo pipefail
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd); cd "$repo_root"
source scripts/load_env.sh
if [[ $# -ne 3 ]]; then echo "usage: $0 SYNTHESIS_DIR WORKLOAD.json OUTPUT_DIR" >&2; exit 2; fi
synth_dir=$1; workload=$2; out_dir=$3; mkdir -p "$out_dir"
cell_models=${AGCWS_SKY130_CELL_MODELS:-/opt/eda/ChipSTA/examples/sky130_hd.v}
primitive_models=${AGCWS_SKY130_PRIMITIVES:-/opt/eda/ChipSTA/examples/sky130_hd_primitives.v}
test -f "$cell_models" || { echo "missing AGCWS_SKY130_CELL_MODELS: $cell_models" >&2; exit 2; }
test -f "$primitive_models" || { echo "missing AGCWS_SKY130_PRIMITIVES: $primitive_models" >&2; exit 2; }
export AGCWS_DMA_WORKLOAD=$(realpath "$workload")
build_dir=${AGCWS_GLS_BUILD_DIR:-out/.cache/axi-dma-gls}; mkdir -p "$build_dir"
PYTHONPATH="$repo_root/third_party/harnesses${PYTHONPATH:+:$PYTHONPATH}" \
  "$repo_root/.venv/bin/python" - "$repo_root" "$synth_dir" "$out_dir" "$cell_models" "$primitive_models" <<'PY'
import sys
from pathlib import Path
from cocotb_test.simulator import run
repo, synth, out, cells, primitives = map(Path, sys.argv[1:])
run(verilog_sources=[synth / "mapped.v", cells, primitives],
    toplevel="axi_dma", module="axi_dma_coupled_tb", simulator="icarus",
    sim_build=str(out / "sim_build"), waves=True,
    compile_args=["-DUNIT_DELAY="])
PY
fst=$(find "$out_dir/sim_build" -maxdepth 2 -name '*.fst' -print -quit)
test -n "$fst" || { echo "AXI GLS produced no FST" >&2; exit 1; }
"${AGCWS_FST2VCD:-fst2vcd}" "$fst" > "$out_dir/activity.vcd"
PYTHONPATH="$repo_root/src" "$repo_root/.venv/bin/python" scripts/parse_vcd_activity.py \
  "$out_dir/activity.vcd" --clock clk --output "$out_dir/activity.json"
echo "AXI_DMA_GLS_DONE out=$out_dir"
