#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
out_dir=${1:-out/aes-core-smoke}
blocks=${2:-1}
idle_cycles=${3:-0}
pattern=${4:-0}
timeout_s=${AGCWS_SIM_TIMEOUT_S:-60}
max_waveform_bytes=${AGCWS_MAX_WAVEFORM_BYTES:-268435456}
mkdir -p "$out_dir"
build_dir=${AGCWS_SIM_BUILD_DIR:-"$out_dir/obj_dir"}
if [[ "$build_dir" != /* ]]; then
  build_dir="$repo_root/$build_dir"
fi
mkdir -p "$build_dir"
python3 scripts/resolve_sv_sources.py --top aes_cipher_core > "$out_dir/sources.list"
sim_binary="$build_dir/aes_core_smoke"
if [[ ! -x "$sim_binary" ]]; then
verilator --binary --trace-vcd --timing --sv --top-module aes_core_smoke \
  -Wno-fatal -Wno-WIDTHTRUNC \
  -Mdir "$build_dir" -o "$sim_binary" \
  -Ithird_party/opentitan/hw/ip/aes/rtl \
  -Ithird_party/opentitan/hw/ip/prim/rtl \
  -Ithird_party/opentitan/hw/ip/prim_generic/rtl \
  -Ithird_party/opentitan/hw/ip/edn/rtl \
  -Ithird_party/opentitan/hw/ip/csrng/rtl \
  -Ithird_party/opentitan/hw/ip/entropy_src/rtl \
  $(<"$out_dir/sources.list") experiments/aes_core_smoke.sv
fi
: > "$out_dir/activity.vcd"
idle_args=("+BLOCKS=$blocks" "+IDLE=$idle_cycles" "+PATTERN=$pattern")
if [[ -n "${AGCWS_IDLE_PATTERN:-}" ]]; then
  IFS=',' read -r -a idle_values <<< "$AGCWS_IDLE_PATTERN"
  for index in "${!idle_values[@]}"; do
    idle_args+=("+IDLE${index}=${idle_values[$index]}")
  done
fi
timeout --kill-after=5s "${timeout_s}s" bash -c \
  "cd \"$out_dir\" && \"$sim_binary\" ${idle_args[*]}" \
  > "$out_dir/run.log" 2>&1
if [[ ! -s "$out_dir/activity.vcd" ]]; then
  echo "simulation did not produce a non-empty VCD" >&2
  exit 1
fi
waveform_bytes=$(stat -c '%s' "$out_dir/activity.vcd")
if (( waveform_bytes > max_waveform_bytes )); then
  echo "VCD exceeds AGCWS_MAX_WAVEFORM_BYTES: $waveform_bytes" >&2
  exit 1
fi
if ! head -c 64 "$out_dir/activity.vcd" | grep -q '\$date\|\$version'; then
  echo "VCD header is not recognized" >&2
  exit 1
fi
python3 scripts/parse_vcd_activity.py "$out_dir/activity.vcd" \
  --windows 8 --output "$out_dir/activity.json"
