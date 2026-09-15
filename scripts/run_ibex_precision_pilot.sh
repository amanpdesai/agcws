#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python -u -m agcws.pipeline run \
  --directory out/ibex-precision-pilot-v1 --execute --allow-paid \
  2>&1 | tee -a out/ibex-precision-pilot-v1/runner.log
status=${PIPESTATUS[0]}
printf 'AGCWS_PILOT_EXIT_CODE=%s\n' "$status" | tee -a out/ibex-precision-pilot-v1/runner.log
exit "$status"
