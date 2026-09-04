#!/usr/bin/env bash
set -euo pipefail

root=${1:-out/vertex-aes-matrix-10}
budget=${2:-200}
calibration=${3:?usage: $0 OUTPUT_DIR BUDGET AES_ACTIVITY_CALIBRATION_JSON}
python_bin=${AGCWS_PYTHON:-.venv/bin/python}

if [[ ! -f "$calibration" ]]; then
  printf 'calibration artifact not found: %s\n' "$calibration" >&2
  exit 2
fi

p_min=$(jq -r '.p_min // empty' "$calibration")
p_max=$(jq -r '.p_max // empty' "$calibration")
metric=$(jq -r '.power_metric // empty' "$calibration")
if [[ -z "$p_min" || -z "$p_max" || "$metric" != "total_transitions_per_clock_edge" ]]; then
  printf 'invalid AES activity calibration artifact: %s\n' "$calibration" >&2
  exit 2
fi
if ! awk -v lo="$p_min" -v hi="$p_max" 'BEGIN { exit !((hi > lo) && (hi - lo >= 10)) }'; then
  printf 'refusing narrow AES envelope %.6f..%.6f from %s\n' "$p_min" "$p_max" "$calibration" >&2
  exit 2
fi

mkdir -p "$root"
printf 'using AES calibration %s: %s..%s\n' "$calibration" "$p_min" "$p_max"
for seed in 0 1 2 3 4 5 6 7 8 9; do
  out="$root/seed-$seed"
  if [[ -f "$out/summary.json" ]] && jq -e --argjson budget "$budget" '.budget == $budget' "$out/summary.json" >/dev/null; then
    continue
  fi
  if timeout --signal=TERM 1200s "$python_bin" scripts/run_aes_search.py \
    out/aes-core-synthesis-final2 --policy vertex \
    --calibration "$calibration" \
    --budget "$budget" --seed "$seed" --out "$out"; then
    printf 'seed %s complete\n' "$seed"
  else
    status=$?
    printf 'seed %s failed (status %s); continuing\n' "$seed" "$status" >&2
  fi
done
