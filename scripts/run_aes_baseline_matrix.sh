#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "usage: $0 SYNTHESIS_DIR P_MIN P_MAX [OUTPUT_DIR]" >&2
  exit 2
fi

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
synthesis_dir=$1
p_min=$2
p_max=$3
output_dir=${4:-out/aes-baseline-matrix}
budget=${AGCWS_SEARCH_BUDGET:-200}
seeds=${AGCWS_SEARCH_SEEDS:-0}
python_bin=${AGCWS_PYTHON:-python3}
target=${AGCWS_SEARCH_TARGET:-0.5}
epsilon=${AGCWS_SEARCH_EPSILON:-0.05}
targets=${AGCWS_SEARCH_TARGETS:-$target}
calibration=${AGCWS_CALIBRATION:-}
policies=${AGCWS_SEARCH_POLICIES:-"random mutation evolutionary one-shot-agent offline-hybrid"}
resume=${AGCWS_RESUME:-0}
export PYTHONPATH="$repo_root/src${PYTHONPATH:+:$PYTHONPATH}"

for target_value in $targets; do
  target_dir="$output_dir/target-$target_value"
  for seed in $seeds; do
    for policy in $policies; do
      run_dir="$target_dir/seed-$seed/$policy"
      if [[ "$resume" == "1" && -f "$run_dir/summary.json" && -f "$run_dir/trials.jsonl" ]]; then
        completed=$(wc -l < "$run_dir/trials.jsonl")
        if [[ "$completed" -eq "$budget" ]]; then
          echo "resuming: keeping complete $run_dir ($completed proposals)"
          continue
        fi
        echo "resuming: rerunning incomplete $run_dir ($completed/$budget proposals)" >&2
      fi
      search_args=("$synthesis_dir" --policy "$policy" \
        --fidelity activity --target "$target_value" --epsilon "$epsilon" \
        --budget "$budget" --seed "$seed" --out "$run_dir")
      if [[ -n "$calibration" ]]; then
        search_args+=(--calibration "$calibration")
      else
        search_args+=(--p-min "$p_min" --p-max "$p_max")
      fi
      "$python_bin" scripts/run_aes_search.py "${search_args[@]}"
    done
  done
done

"$python_bin" scripts/aggregate_runs.py "$output_dir" --out "$output_dir/aggregate.json"
echo "AES_BASELINE_MATRIX_DONE aggregate=$output_dir/aggregate.json"
