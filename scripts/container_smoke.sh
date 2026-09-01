#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
source scripts/load_env.sh
artifact_root=${AGCWS_ARTIFACT_ROOT:-out}

command -v "${AGCWS_VERILATOR:-verilator}" >/dev/null
command -v "${AGCWS_YOSYS:-yosys}" >/dev/null
command -v "${AGCWS_OPENSTA:-sta}" >/dev/null
"${AGCWS_OPENSTA:-sta}" -version >/dev/null
command -v "${AGCWS_RISCV_GCC:-riscv64-unknown-elf-gcc}" >/dev/null
"${AGCWS_RISCV_GCC:-riscv64-unknown-elf-gcc}" --version >/dev/null
if [[ -n "${AGCWS_SLANG_PLUGIN:-}" ]]; then
  test -f "$AGCWS_SLANG_PLUGIN"
  "${AGCWS_YOSYS:-yosys}" -Q -p "plugin -i $AGCWS_SLANG_PLUGIN; help read_slang" >/dev/null
fi
test -f "${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}"
test -f "${AGCWS_LIBERTY_NANGATE45:-third_party/liberty/nangate45/Nangate45_typ.lib}"
python3 scripts/resolve_ibex_sources.py --core lowrisc:ibex:ibex_top --out "$artifact_root/container-ibex-sources" >/dev/null
python3 scripts/check_ibex_verilator.py "$artifact_root/container-ibex-sources/sources.json" >/dev/null
python3 scripts/chia_smoke.py >/dev/null
PYTHONPATH=src python3 scripts/chia_node_smoke.py >/dev/null
python3 scripts/inspect_liberty.py "${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}" >/dev/null
mkdir -p "$artifact_root/container-memory-smoke"
iverilog -g2012 -s agcws_axi_memory_model_smoke \
  -o "$artifact_root/container-memory-smoke/memory.vvp" \
  third_party/harnesses/axi_memory_model.v \
  third_party/harnesses/axi_memory_model_smoke.v
(cd "$artifact_root/container-memory-smoke" && vvp memory.vvp >/dev/null)
PYTHONPATH=src python3 scripts/run_axi_dma_workload.py \
  experiments/workloads/axi_dma_smoke.json "$artifact_root/container-axi-dma-smoke" >/dev/null
mkdir -p "$artifact_root/container-ibex-smoke"
python3 scripts/generate_ibex_workload.py "$artifact_root/container-ibex-smoke/workload.json"
bash scripts/run_ibex_workload.sh \
  "$artifact_root/container-ibex-smoke/workload.json" "$artifact_root/container-ibex-smoke" >/dev/null
python3 scripts/verify_artifact.py "$artifact_root/container-ibex-smoke" >/dev/null
echo "AGCWS_CONTAINER_SMOKE_OK"
