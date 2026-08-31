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
fst2vcd=${AGCWS_FST2VCD:-fst2vcd}

mkdir -p "$out_dir"
workload_abs=$(cd "$(dirname "$workload")" && pwd)/$(basename "$workload")
if [[ "$workload_abs" != "$(cd "$out_dir" && pwd)/workload.json" ]]; then
  cp "$workload" "$out_dir/workload.json"
fi
PYTHONPATH=src "${AGCWS_PYTHON:-python3}" scripts/compile_ibex_workload.py \
  "$workload" "$out_dir/workload.elf" --gcc "$gcc" --objcopy "$objcopy"

if [[ ! -x "$sim" ]]; then
  command -v fusesoc >/dev/null
  (cd "$ibex_root" && fusesoc --cores-root=. run --target=sim --setup --build lowrisc:ibex:ibex_simple_system)
fi

sim_dir=$(cd "$(dirname "$sim")" && pwd)
elf_abs=$(cd "$(dirname "$out_dir/workload.elf")" && pwd)/$(basename "$out_dir/workload.elf")
(cd "$out_dir" && "$sim_dir/Vibex_simple_system" \
  --meminit=ram,"$elf_abs" -t > simulator.stdout 2>&1)

test -s "$out_dir/ibex_simple_system_pcount.csv"
test -s "$out_dir/sim.fst"
test -f "$out_dir/ibex_simple_system.log"
test -f "$out_dir/trace_core_00000000.log"

# FuseSoC's Ibex target emits FST.  Convert it to the repository-standard VCD
# when the converter is installed (the production container supplies it).
# Keeping this conditional preserves the lightweight simulator smoke path on
# hosts that only need functional execution.
if command -v "$fst2vcd" >/dev/null 2>&1; then
  # Debian's fst2vcd emits to stdout unless -o is supplied.
  "$fst2vcd" -o "$out_dir/activity.vcd" "$out_dir/sim.fst"
  test -s "$out_dir/activity.vcd"
  PYTHONPATH=src "${AGCWS_PYTHON:-python3}" - "$out_dir/activity.vcd" <<'PY'
import sys
from pathlib import Path
from agcws.nodes.activity import parse_vcd

path = Path(sys.argv[1])
activity = parse_vcd(path, clock_name="clk_i", windows=16)
(path.parent / "activity.json").write_text(__import__("json").dumps(activity, indent=2, sort_keys=True) + "\n")
PY
fi
PYTHONPATH=src "${AGCWS_PYTHON:-python3}" scripts/write_ibex_result.py \
  "$out_dir" "$workload"
echo "AGCWS_IBEX_WORKLOAD_OK"
