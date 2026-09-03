#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
source scripts/load_env.sh
if [[ $# -lt 2 || $# -gt 4 ]]; then
  echo "usage: $0 SYNTHESIS_DIR WAVEFORM.vcd [OUTPUT_DIR] [LIBERTY]" >&2
  exit 2
fi
synth_dir=$1
waveform=$2
out_dir=${3:-"$synth_dir/power"}
liberty=${4:-${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}}
mkdir -p "$out_dir"

cat > "$out_dir/power.tcl" <<EOF
read_liberty $liberty
read_verilog $synth_dir/mapped.v
link_design aes_cipher_core
create_clock -name clk_i -period 10 [get_ports clk_i]
read_vcd -scope "${AGCWS_VCD_SCOPE:-aes_core_smoke/dut}" $waveform
report_power -digits 12
report_activity_annotation -report_unannotated
EOF
if [[ -n "${AGCWS_OPENSTA_TIMEOUT_S:-}" ]]; then
  timeout --kill-after=5s "${AGCWS_OPENSTA_TIMEOUT_S}s" "${AGCWS_OPENSTA:-sta}" -exit "$out_dir/power.tcl" > "$out_dir/power.rpt" 2>&1
else
  "${AGCWS_OPENSTA:-sta}" -exit "$out_dir/power.tcl" > "$out_dir/power.rpt" 2>&1
fi
awk '/^Annotated [0-9]+ pin activities\./ {print $0}' "$out_dir/power.rpt" > "$out_dir/annotation.rpt"
echo "OPENSTA_DONE report=$out_dir/power.rpt"
