# Reproducibility scripts

Scripts in this directory are small, inspectable entry points used by local
and container tasks. They must not embed machine-specific EDA paths; use the
repository `.env` settings or command-line arguments.

```bash
python scripts/inspect_liberty.py "$AGCWS_LIBERTY"
python scripts/aes_sources.py
python scripts/resolve_sv_sources.py --top aes_cipher_core
python scripts/resolve_sv_sources.py --top aes --include-generated
bash scripts/lint_aes_core.sh
bash scripts/run_aes_core_smoke.sh
python3 scripts/run_aes_workload.py experiments/workloads/aes_zero_blocks.json
```

Aggregate completed search runs without dropping unsolved runs:

```bash
python3 scripts/aggregate_runs.py out/aes-runs --out out/aes-runs/aggregate.json
```

Each search directory contains `summary.json` with the pre-registered
best-so-far AUC, solve status, right-censored evaluations-to-target, policy,
design, and seed. The aggregator groups by policy and canonical design name.

Run the declared local baseline matrix (override `AGCWS_SEARCH_BUDGET` and
space-separated `AGCWS_SEARCH_SEEDS` as needed):

```bash
bash scripts/run_aes_baseline_matrix.sh out/aes-core-synthesis-final4 \
  128.726293 130.431250 out/aes-baselines
```

Set `AGCWS_PYTHON` when the host uses a specific virtual environment; the
driver also exports the repository `src/` path for direct checkouts.

The AES source manifest is intentionally separate from the future TileLink
harness. OpenTitan's `aes` top level depends on common OpenTitan primitive and
TileLink packages plus generated lifecycle constants. The manifest is an
auditable first-pass compile set; the harness command must still select the
configuration-specific generated packages and remove unrelated primitive
implementations before treating lint as a pass.
## AES synthesis

Generate the cached AES core netlist against the configured Liberty file:

```bash
bash scripts/synthesize_aes_core.sh out/aes-core-synthesis
```

The output contains the resolved source list, Yosys log, mapped netlist,
statistics, checksums, and a manifest. The netlist is a design-level artifact;
candidate workloads must not trigger synthesis again.

Convert a simulation waveform to backward SAIF for OpenSTA:

```bash
bash scripts/vcd_to_saif.sh out/aes-workload/activity.vcd out/aes-workload/activity.saif
```

Run the first OpenSTA smoke evaluation against a mapped netlist:

Check that every mapped cell instance is characterized by the selected Liberty:

```bash
python3 scripts/check_liberty_coverage.py \
  out/aes-core-synthesis-final4/stat.json "$AGCWS_LIBERTY"
```

```bash
bash scripts/run_opensta_aes.sh out/aes-core-synthesis-final4 \
  out/aes-core-smoke-bounded/activity.vcd
```

Evaluate one workload through the complete simulation and power path:

```bash
python3 scripts/evaluate_aes_workload.py experiments/workloads/aes_zero_blocks.json \
  out/aes-core-synthesis-final4 --out out/aes-evaluation
```

For resumable, content-addressed evaluation tasks:

```bash
PYTHONPATH=src python3 scripts/run_aes_task.py \
  experiments/workloads/aes_zero_blocks.json out/aes-core-synthesis-final4 \
  --out out/tasks
```

The task key includes the workload and synthesis-manifest digests. Re-running
the command resumes a completed task; changed inputs produce a new task.

Check evaluator determinism before freezing calibration parameters:

```bash
PYTHONPATH=src python3 scripts/check_aes_determinism.py \
  experiments/workloads/aes_zero_blocks.json out/aes-core-synthesis-final4
```

Plot recorded per-cycle and coarse-window activity without rerunning the tools:

```bash
python3 analysis/plot_activity.py out/aes-determinism/run-0/activity.json \
  --out out/figures/aes_activity.png
```

Compute the Slice-4 envelope and provisional useful-work floor:

```bash
PYTHONPATH=src python3 scripts/calibrate_aes.py \
  out/aes-calibration-10/corpus.jsonl --out out/aes-calibration-10/calibration.json
```

Measure the pre-registered random-search solve fraction before comparative runs:

```bash
PYTHONPATH=src python3 scripts/run_aes_scalar_calibration.py \
  out/aes-core-synthesis-final4 --out out/aes-scalar-calibration
```

The calibration is resumable: completed seed/target cells are marked with a
local `summary.json` and skipped on subsequent invocations.
Independent seed ranges may be run in parallel with separate output roots.

Simulator compilation is shared through `AGCWS_SIM_BUILD_DIR` by default, while
each task retains isolated waveform, activity, and result artifacts.
