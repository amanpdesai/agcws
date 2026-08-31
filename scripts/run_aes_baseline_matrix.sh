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
export PYTHONPATH="$repo_root/src${PYTHONPATH:+:$PYTHONPATH}"

for seed in $seeds; do
  for policy in random mutation evolutionary offline-hybrid; do
    run_dir="$output_dir/seed-$seed/$policy"
      "$python_bin" scripts/run_aes_search.py "$synthesis_dir" --policy "$policy" \
      --fidelity activity --target "$target" --epsilon "$epsilon" \
      --p-min "$p_min" --p-max "$p_max" \
      --budget "$budget" --seed "$seed" --out "$run_dir"
  done
done

"$python_bin" scripts/aggregate_runs.py "$output_dir" --out "$output_dir/aggregate.json"
echo "AES_BASELINE_MATRIX_DONE aggregate=$output_dir/aggregate.json"
