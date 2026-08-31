#!/usr/bin/env bash
set -euo pipefail
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
source scripts/load_env.sh
python_bin=${AGCWS_PYTHON:-python3}
export PYTHONPATH="$repo_root/src${PYTHONPATH:+:$PYTHONPATH}"
if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "usage: $0 CORPUS_DIR CROSS_PDK_DIR OUTPUT_DIR [LIBERTY_NANGATE]" >&2
  exit 2
fi
corpus=$1; pdk_dir=$2; output=$3
sky_lib=${AGCWS_LIBERTY:-third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib}
nangate_lib=${4:-${AGCWS_LIBERTY_NANGATE45:-third_party/liberty/nangate45/Nangate45_typ.lib}}
sky_synth="$pdk_dir/sky130hd-synthesis"; nangate_synth="$pdk_dir/nangate45-synthesis"
[[ -f "$sky_synth/mapped.v" && -f "$nangate_synth/mapped.v" ]] || { echo "both PDK netlists are required below $pdk_dir" >&2; exit 2; }
mkdir -p "$output/sky-reports" "$output/nangate-reports"
shopt -s nullglob
workloads=("$corpus"/trial-*/workload.json)
(( ${#workloads[@]} >= 2 )) || { echo "corpus needs at least two trial workloads" >&2; exit 2; }
for workload in "${workloads[@]}"; do
  trial=$(basename "$(dirname "$workload")"); waveform="$corpus/$trial/activity.vcd"
  [[ -f "$waveform" ]] || { echo "missing waveform: $waveform" >&2; exit 1; }
  bash scripts/run_opensta_aes.sh "$sky_synth" "$waveform" "$output/sky-reports/$trial" "$sky_lib" >/dev/null
  bash scripts/run_opensta_aes.sh "$nangate_synth" "$waveform" "$output/nangate-reports/$trial" "$nangate_lib" >/dev/null
done
"$python_bin" scripts/validate_aes_pdk_corpus.py "$corpus" "$output/sky-reports" "$output/nangate-reports" --out "$output/corpus-validation.json"
"$python_bin" scripts/write_aes_pdk_manifest.py "$corpus" "$sky_synth" "$nangate_synth" \
  "$sky_lib" "$nangate_lib" --out "$output/run-manifest.json" >/dev/null
echo "AES_PDK_CORPUS_DONE output=$output"
