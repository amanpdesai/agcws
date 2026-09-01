# Reproducibility scripts

Scripts in this directory are small, inspectable entry points used by local
and container tasks. They must not embed machine-specific EDA paths; use the
repository `.env` settings or command-line arguments.

## Memory-aware synthesis

`inventory_yosys_memories.py` preserves inferred memories through Yosys and
records their geometry. `generate_memory_collateral.py` turns that inventory
into deterministic macro contracts and a manifest. The output is contract-only
until a verified bsg_fakeram wrapper and Liberty model are supplied; it is not
valid input for power claims by itself.

```bash
make inventory-memories MEMORY_TOP=ram MEMORY_SOURCE=path/to/ram.sv
make memory-collateral MEMORY_TOP=ram MEMORY_INVENTORY=out/memory-inventory/ram.json
```

The second command also writes `bsg_fakeram.json`, in the native generator
configuration shape. Run the pinned generator explicitly after reviewing the
inventory and selecting the matching technology parameters:

```bash
python3 third_party/bsg_fakeram/scripts/run.py \
  out/memory-collateral/ram/bsg_fakeram.json \
  --output_dir out/memory-collateral/ram/generated
```

It also writes `memory_libmap.txt` for Yosys. Use that file only after checking
that the inferred memory is truly single-clock synchronous 1RW and that the
generated macro's logical wrapper preserves the design's read-during-write
behavior.

To run an explicitly reviewed mapping experiment, set
`AGCWS_MEMORY_LIBMAP` to that file before invoking either synthesis script.
The scripts run `memory_libmap` before `memory_map` and record the selected file
and digest in `manifest.json`. Leave the variable unset for the baseline; a
contract-only or semantically incompatible bundle must never be used for a
reported power result.

Existing design synthesis remains unchanged until port semantics, mapping, and
characterization are validated, keeping baseline results comparable.

The host compatibility frontend is suitable for reduced/simple SystemVerilog
closures only. Full OpenTitan AES synthesis requires the pinned Slang plugin
provided by `docker/Dockerfile`; if that plugin is absent, a host AES run may
fail during parsing and must not be treated as a synthesis result.

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

Run the DMA activity search matrix with isolated output per policy:

```bash
make axi-dma-search DMA_POLICIES=random,mutation,evolutionary BUDGET=200
```

The matrix writes `matrix.json` plus one directory per policy. Every policy
uses the same proposal-counted budget and coupled simulation/activity oracle.

Each search directory contains `summary.json` with the pre-registered
best-so-far AUC, solve status, right-censored evaluations-to-target, policy,
design, and seed. The aggregator groups by policy and canonical design name.

Generate a deterministic convergence figure from completed runs:

```bash
make plot-search-curves BASELINE_DIR=out/aes-baseline-matrix
```

To produce both the aggregate statistics and convergence figure in one
reproducible step, use:

```bash
make analyze-baseline \
  BASELINE_DIR=out/aes-baseline-matrix-complete \
  ANALYSIS_DIR=out/final-analysis
```

This command preserves right-censored runs and writes `aggregate.json`,
`convergence.png`, and its machine-readable plot summary below
`ANALYSIS_DIR`. It does not infer that the input is a complete factorial
study; the experiment manifest and plan remain authoritative for that claim.

Validate a completed AES corpus against both pre-built PDK netlists. The
corpus must contain `trial-*/workload.json`; each report root must contain the
matching `trial-*/power.rpt`. The command fails closed if a workload or either
PDK report is missing, and records paired power ranges plus Spearman rank
agreement:

Invoke the script directly with the two report roots:

```bash
python3 scripts/validate_aes_pdk_corpus.py CORPUS SKY_REPORTS NANGATE_REPORTS \
  --out out/aes-pdk-corpus-validation.json
```

To generate those paired reports from an existing corpus and the two netlists,
use the wrapper (it honors `AGCWS_PYTHON` for the active virtual environment):

```bash
make run-aes-pdk-corpus \
  CORPUS_DIR=out/aes-random-corpus \
  CROSS_PDK_DIR=out/aes-cross-pdk
```

The wrapper writes report directories and `corpus-validation.json` below
`AGCWS_ARTIFACT_ROOT/aes-pdk-corpus`.

Run the declared local baseline matrix (override `AGCWS_SEARCH_BUDGET` and
space-separated `AGCWS_SEARCH_SEEDS` as needed):

```bash
bash scripts/run_aes_baseline_matrix.sh out/aes-core-synthesis-final4 \
  128.726293 130.431250 out/aes-baselines
```

Long matrices can resume without redoing complete cells. Set
`AGCWS_RESUME=1`; a cell is reused only when both `summary.json` exists and
`trials.jsonl` contains exactly the declared proposal budget. Incomplete cells
are rerun, preserving the same proposal-counted budget for every policy.

Set `AGCWS_PYTHON` when the host uses a specific virtual environment; the
driver also exports the repository `src/` path for direct checkouts.
`AGCWS_SEARCH_TARGET` and `AGCWS_SEARCH_EPSILON` select the scalar target and
tolerance without modifying the driver (defaults: `0.5` and `0.05`). For the
pre-registered target set, use `AGCWS_SEARCH_TARGETS='0.10 0.25 0.50 0.75 0.90'`;
each target receives an isolated output directory.

The AES source manifest is intentionally separate from the future TileLink
harness. OpenTitan's `aes` top level depends on common OpenTitan primitive and
TileLink packages plus generated lifecycle constants. The manifest is an
auditable first-pass compile set; the harness command must still select the
configuration-specific generated packages and remove unrelated primitive
implementations before treating lint as a pass.

## Ibex source closure

Resolve the pinned Ibex simple-system dependency graph through FuseSoC and
write a content-hashed SystemVerilog manifest:

```bash
make chia-install
make verification-install
make resolve-ibex-sources
```

The output is `out/ibex-sources/sources.json`, including the hashed RTL files
and include directories required for single-unit Slang compilation. It is the
input inventory for the upcoming Ibex synthesis flow; the script fails if
FuseSoC references a missing source instead of silently producing a partial
design. `verification-install` installs the pinned FuseSoC dependency into the
project virtualenv. Generated FuseSoC files are written below the configured
artifact root in `fusesoc-work/`, not into the RTL checkout.

Use the selectable Make variables to resolve a specific closure. For the
standalone CPU boundary, the reproducible container command is:

```bash
make resolve-ibex-sources IBEX_CORE=lowrisc:ibex:ibex_core
make probe-ibex-synthesis \
  IBEX_SOURCES=out/ibex-core-sources/sources.json IBEX_TOP=ibex_core
```

For `make synthesize-ibex-core IBEX_TOP=ibex_core`, the target intentionally
ignores the default `IBEX_SOURCES` value and resolves a fresh, isolated
`lowrisc:ibex:ibex_core` closure under the artifact root. This prevents the
simple-system workload closure from contaminating core-only synthesis. Use the
`probe-ibex-synthesis` command above when you specifically need to inspect an
already-resolved manifest.

The default remains `lowrisc:ibex:ibex_simple_system` / `ibex_top`, which is
the closure used by the current workload runner. `IBEX_CORE`, `IBEX_SOURCES`,
and `IBEX_TOP` are recorded in the generated probe manifest so a failed or
successful frontend boundary can be reproduced exactly.

To capture the current Ibex gate-level integration diagnostic, run
`make resolve-ibex-sources` followed by `make probe-ibex-synthesis`.
The probe writes `manifest.json` and `yosys.log` and intentionally exits
nonzero when the frontend cannot elaborate the pinned closure.

For the supported RTL-boundary check, run `make check-ibex-rtl`. It resolves the
same closure and lints it with Verilator; this is intentionally separate from
the Slang/Yosys synthesis-front-end experiment.
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

The calibration input is explicit; use `--calibration calibration.json` with
`run_aes_scalar_calibration.py` when the corpus is not in the legacy default
location.
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

Run and validate the functional Ibex artifact:

```bash
make run-ibex
make verify-ibex IBEX_ARTIFACT=out/ibex
```

Calibrate the Ibex RTL-activity envelope before selecting scalar targets:

```bash
python3 scripts/calibrate_ibex_activity.py --samples 10 --seed 0 \
  --out out/ibex-activity-calibration
```

Pass the resulting `p_min` and `p_max` to `run_ibex_search.py`; these are
normalized activity units, not watts. The runner supports `random`, `mutation`,
`evolutionary`, `offline-agent`, `one-shot-agent`, and `offline-hybrid`; the
offline agent arms are deterministic smoke/comparison surrogates, not Vertex
AI evidence.

Run the proposal-counted Ibex activity search (inside the verification
container, because each proposal compiles and runs the upstream simple-system
simulator):

```bash
python3 scripts/run_ibex_search.py --policy random --p-min 0 --p-max 100 \
  --budget 20 --seed 0 --out out/ibex-search
```

Prefer loading bounds directly from calibration to avoid copying values:

```bash
python3 scripts/run_ibex_search.py --policy random \
  --calibration out/ibex-activity-calibration/calibration.json \
  --budget 20 --seed 0 --out out/ibex-search
```

Run a reproducible seed matrix with isolated outputs:

```bash
python3 scripts/run_ibex_search.py \
  --policies random,mutation,evolutionary,offline-agent,one-shot-agent,offline-hybrid \
  --calibration out/ibex-activity-calibration/calibration.json \
  --budget 200 --seeds 0,1,2,3,4 --out out/ibex-matrix
```

The runner records RTL per-cycle/window toggle activity and simulator
provenance through the shared search contract. `--p-min` and `--p-max` are
activity-envelope bounds, not watts; this path is not an Ibex gate-level
OpenSTA evaluation. Use separate output roots for parallel seeds.

Run the remote CHIA simulation-to-activity acceptance DAG:

```bash
make chia-node-smoke
```
