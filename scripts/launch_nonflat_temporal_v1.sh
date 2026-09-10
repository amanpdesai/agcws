#!/usr/bin/env bash
set -euo pipefail
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
test -f results/nonflat_temporal_v1/smoke_pass.json
test ! -e out/nonflat-temporal-v1/complete.json
exec systemd-run --user --unit=agcws-nonflat-temporal-v1 \
  --description='Frozen Ibex non-flat Pro versus phase-random confirmation' \
  --working-directory="$repo_root" \
  --property=Restart=no --property=RemainAfterExit=yes \
  --property=TimeoutStopSec=180 \
  --property="StandardOutput=append:$repo_root/out/nonflat-temporal-v1/service.log" \
  --property=StandardError=inherit \
  --setenv=OPENBLAS_NUM_THREADS=1 --setenv=PYTHONUNBUFFERED=1 \
  "$repo_root/.venv/bin/python" -m experiments.nonflat_temporal_v1.study run
