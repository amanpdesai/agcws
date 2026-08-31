# Plan

**D1 = 2026-08-29. D23 = 2026-09-20.** Status: `TODO` / `WIP` / `DONE` / `BLOCKED` / `CUT`.

Build one design vertically before widening: AES first, `axi_dma` second, Ibex third. Prove a responsive power oracle before adding the agent or more adapters.

| Slice | Work | By | Status |
|---:|---|---|---|
| 0 | Repo skeleton, docs, container | D2 | DONE |
| 1 | CHIA stock case and Vertex billing | D3 | TODO |
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

Evidence checkpoint (2026-08-31): the image-only container smoke passes, the
AES scalar matrix has completed for five targets and four policies at 200
proposals for two seeds, and achieved-profile temporal/compositional searches
plus finalist OpenSTA validation have executed. These remain preliminary
results; they are not the final multi-design statistical study.

Slice 7 currently has deterministic DMA channel harnesses, a coupled
source-to-destination memory-copy harness with VCD/activity provenance,
workload validation, useful-work gating, and provenance. It also has a
deterministic Ibex JSON-to-ELF compiler and upstream simple-system Verilator
runner. Synthesis/evaluation integration remains before both adapters are
experiment-ready.
The pinned upstream coupled-DMA reference test now passes through the isolated
`make upstream-dma-reference` target; it is a protocol oracle, not the project
runtime, and does not change this milestone's status.

Slice 8 currently exposes random, mutation, evolutionary, and hybrid policies
through the common proposal-counted AES runner. Slice 10 has deterministic AUC,
solve-rate, censoring, validity/cost metrics, and multi-root corpus aggregation;
multi-design runs and figures remain outstanding.

Slice 6 has the common offline-agent and Vertex policy interfaces plus the
frozen generic prompt; Vertex credentials/model billing and a comparative
agent run remain unverified.

Slice 9 has executable AES temporal and compositional search drivers using the
activity oracle, achieved-profile target selection, per-cycle/windowed profiles,
and provenance; the full G4 target study remains. Slice 11 has a rebuildable
Docker image and container smoke test; upstream extraction and PR preparation
remain.
