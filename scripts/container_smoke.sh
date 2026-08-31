#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
source scripts/load_env.sh

command -v "${AGCWS_VERILATOR:-verilator}" >/dev/null
command -v "${AGCWS_YOSYS:-yosys}" >/dev/null
command -v "${AGCWS_OPENSTA:-sta}" >/dev/null
"${AGCWS_OPENSTA:-sta}" -version >/dev/null
if [[ -n "${AGCWS_SLANG_PLUGIN:-}" ]]; then
  test -f "$AGCWS_SLANG_PLUGIN"
  "${AGCWS_YOSYS:-yosys}" -Q -p "plugin -i $AGCWS_SLANG_PLUGIN; help read_slang" >/dev/null
fi
test -f "${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}"
test -f "${AGCWS_LIBERTY_NANGATE45:-third_party/liberty/nangate45/Nangate45_typ.lib}"
python3 scripts/inspect_liberty.py "${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}" >/dev/null
PYTHONPATH=src python3 scripts/run_axi_dma_workload.py \
  experiments/workloads/axi_dma_smoke.json out/container-axi-dma-smoke >/dev/null
echo "AGCWS_CONTAINER_SMOKE_OK"
