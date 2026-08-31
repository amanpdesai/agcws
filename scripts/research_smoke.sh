#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

synthesis_dir=${1:-out/aes-core-synthesis-final4}
artifact_root=${2:-out/research-smoke}
workload=${AGCWS_SMOKE_WORKLOAD:-experiments/workloads/aes_min_scored.json}
python_bin=${AGCWS_PYTHON:-python3}

test -f "$synthesis_dir/manifest.json" || {
  echo "missing synthesis manifest: $synthesis_dir (run make synth-aes first)" >&2
  exit 2
}

rm -f "$artifact_root/evaluation/activity.json" \
      "$artifact_root/evaluation/activity.vcd" \
      "$artifact_root/evaluation/opensta/power.rpt"
mkdir -p "$artifact_root"

PYTHONPATH=src "$python_bin" scripts/evaluate_aes_workload.py \
  "$workload" "$synthesis_dir" --out "$artifact_root/evaluation" >/dev/null
PYTHONPATH=src "$python_bin" scripts/check_aes_determinism.py \
  "$workload" "$synthesis_dir" --out "$artifact_root/determinism" >/dev/null
"$python_bin" analysis/plot_activity.py \
  "$artifact_root/evaluation/activity.json" \
  --out "$artifact_root/activity.png" >/dev/null

# Exercise both profile goal classes through the same activity oracle. Keep the
# smoke budget intentionally small; comparative runs use their own declared
# budgets and output roots.
PYTHONPATH=src "$python_bin" scripts/run_aes_temporal_search.py \
  "$synthesis_dir" --budget "${AGCWS_PROFILE_SMOKE_BUDGET:-8}" --seed 0 \
  --out "$artifact_root/temporal" >/dev/null
PYTHONPATH=src "$python_bin" scripts/run_aes_compositional_search.py \
  "$synthesis_dir" --budget "${AGCWS_PROFILE_SMOKE_BUDGET:-8}" --seed 0 \
  --out "$artifact_root/compositional" >/dev/null

"$python_bin" - "$artifact_root/evaluation" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
activity = json.loads((root / "activity.json").read_text())
power = json.loads((root / "result.json").read_text())
required_activity = ("per_cycle_toggles", "window_toggles", "normalized_windows",
                     "waveform_sha256", "clock_edges")
missing = [key for key in required_activity if key not in activity]
if missing:
    raise SystemExit(f"activity missing required fields: {missing}")
if len(activity["waveform_sha256"]) != 64:
    raise SystemExit("activity waveform_sha256 is not a SHA-256 digest")
if len(activity["normalized_windows"]) != len(activity["window_toggles"]):
    raise SystemExit("normalized activity profile length does not match windows")
if not power.get("valid") or power.get("useful_work", 0) <= 0:
    raise SystemExit("evaluation did not produce a valid useful-work result")
for profile in ("temporal", "compositional"):
    summary = json.loads((root.parent / profile / "summary.json").read_text())
    if summary.get("valid_trials", 0) <= 0 or summary.get("simulations", 0) <= 0:
        raise SystemExit(f"{profile} smoke did not produce valid simulations")
print("AGCWS_RESEARCH_SMOKE_OK")
PY
