# Agentic Goal-Conditioned Workload Synthesis

Given RTL, a legal stimulus interface, and a target dynamic-power profile, an agent synthesizes semantically valid workloads toward that behavior. Targets may be scalar, compositional, or coarse temporal.

Built as a composable [CHIA](https://github.com/ucb-bar/chia) loop for the A³ CHIA Hackathon (MICRO 2026).

## Status

Under active development (2026-08-29 → 2026-09-20). The AES oracle and
bounded search path are runnable; DMA/Ibex adapters and comparative studies
remain in progress.

See `docs/ARCHITECTURE.md` and `docs/PLAN.md`. The current evidence and claim
boundaries are summarized in [`docs/RESULTS.md`](docs/RESULTS.md), and the
report-ready structure is in [`docs/REPORT.md`](docs/REPORT.md).

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
make analyze-baseline BASELINE_DIR=out/aes-baseline-matrix-complete ANALYSIS_DIR=out/final-analysis
make validate-finalists FINALIST_TRIALS=out/aes-baseline-matrix/target-0.50/seed-0/random/trials.jsonl
make cross-pdk-dma DMA_WAVEFORM=out/axi-dma-coupled/activity.vcd
make axi-dma-search BUDGET=200
make infer-dma
PYTHONPATH=src python scripts/run_aes_task.py \
  experiments/workloads/aes_min_scored.json out/aes-core-synthesis-final4
```

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
[`docs/RESULTS.md`](docs/RESULTS.md), including the three-seed DMA aggregate,
paired inference output, and three-seed temporal/compositional profile snapshot.
It also includes the `riscv64-unknown-elf` compiler/binutils pair, FuseSoC,
and the native dependencies needed to build and run the pinned Ibex simulator.

Contributors should start with [`CONTRIBUTING.md`](CONTRIBUTING.md), which
defines the local verification and reproducibility contract.

To verify that an evaluation still matches its recorded inputs:

```bash
make verify-artifact AGCWS_ARTIFACT=out/aes-evaluation
```

This checks the validity/useful-work contract and every recorded input hash.

## License

BSD 3-Clause, matching CHIA.
