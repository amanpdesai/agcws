#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
source scripts/load_env.sh

workload=${1:?usage: run_ibex_workload.sh WORKLOAD_JSON OUT_DIR}
out_dir=${2:?usage: run_ibex_workload.sh WORKLOAD_JSON OUT_DIR}
ibex_root=${AGCWS_IBEX_ROOT:-third_party/ibex}
sim=${AGCWS_IBEX_SIM:-$ibex_root/build/lowrisc_ibex_ibex_simple_system_0/sim-verilator/Vibex_simple_system}
gcc=${AGCWS_RISCV_GCC:-riscv64-unknown-elf-gcc}
objcopy=${AGCWS_RISCV_OBJCOPY:-riscv64-unknown-elf-objcopy}

mkdir -p "$out_dir"
PYTHONPATH=src "${AGCWS_PYTHON:-python3}" scripts/compile_ibex_workload.py \
  "$workload" "$out_dir/workload.elf" --gcc "$gcc" --objcopy "$objcopy"

if [[ ! -x "$sim" ]]; then
  command -v fusesoc >/dev/null
  (cd "$ibex_root" && fusesoc --cores-root=. run --target=sim --setup --build lowrisc:ibex:ibex_simple_system)
fi

sim_dir=$(cd "$(dirname "$sim")" && pwd)
workload_abs=$(cd "$(dirname "$out_dir/workload.elf")" && pwd)/$(basename "$out_dir/workload.elf")
(cd "$out_dir" && "$sim_dir/Vibex_simple_system" \
  --meminit=ram,"$workload_abs" -t > simulator.stdout 2>&1)

test -s "$out_dir/ibex_simple_system_pcount.csv"
test -s "$out_dir/sim.fst"
test -f "$out_dir/ibex_simple_system.log"
test -f "$out_dir/trace_core_00000000.log"
echo "AGCWS_IBEX_WORKLOAD_OK"
