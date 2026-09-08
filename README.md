# Agentic Goal-Conditioned Workload Synthesis

AGCWS investigates whether an agent can synthesize legal hardware workloads for requested activity and power behavior. Search uses RTL activity; matched windowed gate power validates selected temporal finalists, not a power-guided agent advantage.

Built as a composable [CHIA](https://github.com/ucb-bar/chia) loop for the A³ CHIA Hackathon (MICRO 2026).

## Status

Under active development (2026-08-29 → 2026-09-20). A complete held-out
AES/DMA scalar study is archived: 550 runs, 27,500 proposal slots, real Vertex
agent and classical baselines. See [results and limitations](docs/SEMANTIC_RESULTS.md).
The agent beats two DMA baselines under the predeclared corrected tests, but
does not establish superiority or parity against random across designs.
A second frozen [structural temporal study](docs/STRUCTURAL_RESULTS.md) is complete:
160 cells / 5120 slots across AES and DMA, with a shared sequence/repeat/pacing
grammar and typed structural edits. Random has the lowest mean AUC on both
designs; AES agent-only is significantly worse than random (Holm p = 0.03125).
No agent/hybrid superiority or parity is established. All 16 predeclared
finalists pass functionally checked, matched-window GLS validation. A separate
[eight-window power validation](docs/WINDOWED_POWER_RESULTS.md) now covers those
16 finalists and four achieved references: 180 native OpenSTA reports, with
independent boundary/state, duration, annotation and numerical checks.
Selected-case activity-error rankings agree with gate-error rankings within
each target/design group; no general proxy or agent-superiority claim follows.
The AlphaEvolve-inspired population alternative was tested in development and
not selected; this is not a reproduction of AlphaEvolve.

The latest [programmable-Ibex grounding development study](docs/IBEX_TEMPORAL_V4_RESULTS.md)
is complete: 48 cells, 768 slots, executed phase/operand diagnostics and persistent
prediction feedback. The response interface is more reliable, but the grounded
agent does not beat random or improve non-flat target coverage. Its complete
compact archive and every finalist are tracked; this is not held-out confirmation.

A controlled [model × reasoning probe](docs/IBEX_CAPABILITY_V1_RESULTS.md) is now
complete: 72 fixed-context cells / 144 slots. Pro-4096 produces mean next-batch
gain 0.14234 versus random 0.02674 and newly solves four contexts, including two
non-flat cases. This is promising development evidence, not a full-search or
held-out win. See the [research roadmap](docs/RESEARCH_DIRECTIONS.md) and
[frozen-context protocol](docs/IBEX_CAPABILITY_V1_PROTOCOL.md).

A [closed-loop depth study](docs/IBEX_DEPTH_V1_PROTOCOL.md) is now running:
Pro-4096, Flash-4096, random and behavior-coverage, four Ibex targets and three
development seeds, with 16/64/128 proposal prefixes. It is not yet a completed
comparison. The [active-path quality audit](docs/CODE_QUALITY_AUDIT.md) documents
strict accounting, immutable checkpoints and preserved historical dependencies.

Reviewable ledgers and inference are tracked in
[`results/structural_temporal_heldout_v1/`](results/structural_temporal_heldout_v1/),
with matched gate evidence in
[`results/structural_temporal_finalist_validation_v1/`](results/structural_temporal_finalist_validation_v1/).

See `docs/ARCHITECTURE.md` and `docs/PLAN.md`. The current evidence and claim
boundaries are summarized in [`docs/RESULTS.md`](docs/RESULTS.md), and the
four-page working draft is [`paper/report.pdf`](paper/report.pdf), with source
and build instructions in [`paper/README.md`](paper/README.md).

Install the optional plotting dependency with `make analysis-install` before
running `make plot-activity` in a fresh environment.

## Common tasks

The Makefile is a thin operator surface over the reproducible scripts:

```bash
make test
make verify
make inspect-liberty
make inspect-liberties
make synth-aes
make evaluate-aes
make research-smoke
make research-audit
make analyze-baseline BASELINE_DIR=out/aes-baseline-matrix-complete ANALYSIS_DIR=out/final-analysis
make validate-finalists FINALIST_TRIALS=out/aes-baseline-matrix-complete/target-0.50/seed-0/random/trials.jsonl
make cross-pdk-dma DMA_WAVEFORM=out/axi-dma-coupled/activity.vcd
make axi-dma-search BUDGET=200
make infer-dma
make aggregate-temporal-pilot
make aggregate-compositional-pilot
make aggregate-temporal-policy-matrix
make aggregate-compositional-policy-matrix
make plot-temporal-policy-matrix
make plot-compositional-policy-matrix
make audit-profile-matrix
make audit-temporal-profile-matrix
PYTHONPATH=src python scripts/run_aes_task.py \
  experiments/workloads/aes_min_scored.json out/aes-core-synthesis-final4
```

The profile audit targets verify that each aggregate matches its achieved
target manifest, policy set, seed count, and proposal budget. The temporal
audit names both recorded manifest generations because that pilot was assembled
incrementally.

For paired-PDK validation, use the checked-in corpus runner after synthesis:

```bash
make run-aes-pdk-corpus \
  CORPUS_DIR=out/aes-random-corpus \
  CROSS_PDK_DIR=out/aes-cross-pdk \
  AGCWS_ARTIFACT_ROOT=out/aes-pdk-validation
```

The runner emits OpenSTA reports, rank-agreement results, and a
`run-manifest.json` containing the exact tool, netlist, Liberty, workload, and
waveform hashes. Vertex-backed runs additionally require
`AGCWS_GCP_PROJECT` and `AGCWS_GEMINI_MODEL`; `make vertex-preflight` checks
those settings without making a cloud call.

Override `SYNTH_DIR`, `WORKLOAD`, and `EVAL_DIR` for separate task roots;
tool and Liberty paths come from `.env` or container defaults.

For a clean environment, build the image and run its smoke check:

```bash
docker build -f docker/Dockerfile -t agcws:dev .
docker run --rm --user "$(id -u):$(id -g)" agcws:dev bash scripts/container_smoke.sh
```

## Designs

OpenTitan AES (register/data) is runnable. The verilog-axi `axi_dma` adapter
(descriptors) has deterministic read/write harnesses plus a coupled
source-to-destination memory-copy harness with waveform/activity provenance;
top-level DMA synthesis/power evaluation now works for Sky130 and Nangate45;
a five-policy proposal-counted DMA matrix is runnable. Ibex (instruction stream)
now has a deterministic JSON-to-ELF compiler and upstream simple-system
Verilator runner that collects retirement counters and FST traces.

## Reproducibility

The pinned CHIA commit and tool/model provenance are recorded in results and `docs/DECISIONS.md`. Large waveform artifacts are ignored.

Verification is available locally through the Python contract suite, Makefile
smoke targets, and Docker build/smoke test. The container includes the open EDA
flow and copied Liberty inputs; cloud
credentials and optional LLM integrations are exercised only in experiments.

The current verified evidence inventory is maintained in
[`docs/RESULTS.md`](docs/RESULTS.md). Historical pilots are separate from the
completed scalar and structural temporal held-out studies.
It also includes the `riscv64-unknown-elf` compiler/binutils pair, FuseSoC,
and the native dependencies needed to build and run the pinned Ibex simulator.

Contributors should start with [`CONTRIBUTING.md`](CONTRIBUTING.md), which
defines the local verification and reproducibility contract.

To verify that an evaluation still matches its recorded inputs:

```bash
make verify-artifact AGCWS_ARTIFACT=out/aes-evaluation
```

This checks the validity/useful-work contract and every recorded input hash.

For memory-aware synthesis discovery and collateral generation:

```bash
make inventory-memories MEMORY_TOP=<top> MEMORY_SOURCE=<rtl-file>
make memory-collateral MEMORY_TOP=<top> \
  MEMORY_INVENTORY=out/memory-inventory/<top>.json
make audit-memory-collateral \
  MEMORY_COLLATERAL=out/memory-collateral/<top>
make audit-memory-collateral-all
```

Review `memory-macros.json` before enabling any mapping. The generated BSG
configuration may contain explicit physical padding for CACTI constraints, and
the audit rejects unsupported read/write or latency semantics.

## License

BSD 3-Clause, matching CHIA.
