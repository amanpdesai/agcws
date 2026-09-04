#!/usr/bin/env bash
set -euo pipefail

root=${1:-out/vertex-aes-matrix-10}
budget=${2:-200}
python_bin=${AGCWS_PYTHON:-.venv/bin/python}
for seed in 0 1 2 3 4 5 6 7 8 9; do
  out="$root/seed-$seed"
  if [[ -f "$out/summary.json" ]] && grep -q '"budget": '"$budget"',' "$out/summary.json"; then
    continue
  fi
  timeout --signal=TERM 900s "$python_bin" scripts/run_aes_search.py \
    out/aes-core-synthesis-final2 --policy vertex \
    --p-min 128.72379032258064 --p-max 130.43421052631578 \
    --budget "$budget" --seed "$seed" --out "$out"
done
