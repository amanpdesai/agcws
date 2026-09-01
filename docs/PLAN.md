# Plan

**D1 = 2026-08-29. D23 = 2026-09-20.** Status: `TODO` / `WIP` / `DONE` / `BLOCKED` / `CUT`.

Build one design vertically before widening: AES first, `axi_dma` second, Ibex third. Prove a responsive power oracle before adding the agent or more adapters.

| Slice | Work | By | Status |
|---:|---|---|---|
| 0 | Repo skeleton, docs, container | D2 | DONE |
| 1 | CHIA stock case and Vertex billing | D3 | WIP |
| 2 | AES power oracle (G1) | D3 | DONE |
| 3 | AES DSL, validator, runner | D5 | DONE |
| 4 | Random envelope/calibration corpus; apply the pre-registered ε rule, freeze the AES useful-work floor, and record measured values in `DECISIONS.md` | D6 | DONE |
| 5 | Non-LLM scalar loop (G2) | D7 | DONE |
| 6 | Agent policy | D9 | WIP |
| 7 | `axi_dma`, then Ibex | D13 | WIP |
| 8 | Mutation/evolutionary/hybrid baselines | D12 | WIP |
| 9 | Compositional/temporal targets (G4) | D16 | WIP |
| 10 | Statistics and figures | D21 | WIP |
| 11 | Container and upstream PR prep | D21 | WIP |
| 12 | Four-page report | D23 | TODO |

Record non-obvious choices in `DECISIONS.md`, unknowns in `RISKS.md`, and never commit waveform artifacts.

Evidence checkpoint (2026-08-31): the pinned CHIA framework smoke and CHIA
node-DAG smoke both pass (`AGCWS_CHIA_SMOKE_OK` and
`AGCWS_CHIA_NODES_SMOKE_OK`) at commit `d78ad77e4ce7b11523bf15a253a258c0f8795673`.
Vertex billing remains unverified, so Slice 1 is still WIP. The image-only container smoke passes, the
AES scalar matrix has completed for five targets and five policies at 200
proposals and ten seeds per cell, and achieved-profile temporal/compositional
searches plus finalist OpenSTA validation have executed. These remain
preliminary results; they are not the final multi-design statistical study.
The public `make baseline-matrix` entry point also completed a five-policy AES
smoke at 20 proposals per arm, with 20 valid simulations per policy and a
machine-readable aggregate; this validates orchestration, not performance.

Slice 7 currently has deterministic DMA channel harnesses, a coupled
source-to-destination memory-copy harness with VCD/activity provenance,
workload validation, useful-work gating, provenance, and Sky130/Nangate45
synthesis/OpenSTA validation. It also has a
deterministic Ibex JSON-to-ELF compiler and upstream simple-system Verilator
runner, with both Ibex FuseSoC source closures fingerprinted. Comparative DMA
workload runs and full Ibex synthesis/power integration remain before the
widened experiment is complete. The full 91-source Ibex closure now passes
Verilator lint in the reproducible container. The pinned Slang/Yosys synthesis
The standalone `lowrisc:ibex:ibex_core` Slang/Yosys frontend probe now
elaborates and maps successfully from an isolated artifact root. The default
`lowrisc:ibex:ibex_simple_system` wrapper still fails at its own elaboration
boundary; no Ibex netlist or power result is treated as valid until synthesis
and mapping are completed for the selected closure.
The pinned upstream coupled-DMA reference test now passes through the isolated
`make upstream-dma-reference` target; it is a protocol oracle, not the project
runtime, and does not change this milestone's status.

Slice 8 currently exposes random, mutation, evolutionary, one-shot-agent, and
hybrid policies through the common proposal-counted runner. Slice 10 has deterministic AUC,
solve-rate, censoring, validity/cost metrics, multi-root corpus aggregation, and
deterministic search-curve plotting. The DMA matrix has completed for five
policies, 200 proposals, and five seeds; the complete multi-design statistical
study remains outstanding.

Slice 6 has the common offline-agent and Vertex policy interfaces plus the
frozen generic prompt. The offline agent has completed a real AES smoke run
under the shared evaluator budget; Vertex credentials/model billing and a
comparative cloud-agent run remain unverified.

Latest verification checkpoint (2026-09-01): `make verify` passes with 181
tests passed and one skipped, Ruff clean, a valid reproducibility audit, and
valid AES/AXI artifacts. Checked-in Sky130 HD and Nangate45 Liberty files both
contain characterized `internal_power`, rise/fall power, leakage, capacitance,
and clock-gating data. The AES cross-PDK corpus has 10 shared workloads with
Spearman rank agreement approximately 1.0. DMA cross-PDK reports are retained
as diagnostics because RTL-to-netlist activity annotation is sparse (about
1.31% Sky130 and 0.77% Nangate45 in the recorded finalist run).

The complete declared AES scalar arm (5 policies × 5 targets × 10 seeds) has
now been executed and mechanically verified at 250 run summaries. The full
multi-design/profile factorial study has not been run and must not be
described as complete. The Ibex core frontend
elaborates from an isolated FuseSoC closure, but the bounded Liberty-mapping
wrapper mapping and Ibex gate-level power integration remain unsupported.
Vertex-backed comparative runs remain blocked on
project/model/billing configuration outside the repository.

The corrected coupled-DMA calibration covers three random seeds and 48
valid proposals, with 16 distinct activity values and measured bounds
`19.67403066–19.80286242`; the machine-readable aggregate is
`out/axi-dma-calibration-corrected-3seed.json`. This is calibration evidence
only. The full-budget DMA matrix now covers five policies, 200 proposals, and
five seeds, with paired inference generated; the panel remains small and
underpowered for definitive policy claims.
Five full-budget DMA seeds are now complete, with paired inference generated;
the panel remains small and underpowered for definitive policy claims.

Slice 9 has executable AES temporal and compositional search drivers using the
activity oracle, achieved-profile target selection, per-cycle/windowed profiles,
and provenance. The temporal pilot matrix covers four targets at five policies
and three seeds; the completed compositional matrix covers three targets at five
policies and three seeds with 300 proposal slots per run. These are activity-
oracle comparisons; the full multi-design G4 target factorial and finalist
gate-level validation remain. Slice 11 has a rebuildable
Docker image, container smoke test, reproducibility audit
(`make audit-reproducibility`), and contributor contract; upstream extraction
and PR preparation remain.
