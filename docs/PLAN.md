# Plan

**D1 = 2026-08-29. D23 = 2026-09-20.** Status: `TODO` / `WIP` / `DONE` / `BLOCKED` / `CUT`.

Build one design vertically before widening: AES first, `axi_dma` second, Ibex third. Prove a responsive power oracle before adding the agent or more adapters.

| Slice | Work | By |
|---:|---|---|
| 0 | Repo skeleton, docs, container | D2 |
| 1 | CHIA stock case and Vertex billing | D3 |
| 2 | AES power oracle (G1) | D3 |
| 3 | AES DSL, validator, runner | D5 |
| 4 | Random envelope/calibration corpus; apply the pre-registered ε rule, freeze the AES useful-work floor, and record measured values in `DECISIONS.md` | D6 |
| 5 | Non-LLM scalar loop (G2) | D7 |
| 6 | Agent policy | D9 |
| 7 | `axi_dma`, then Ibex | D13 | WIP |
| 8 | Mutation/evolutionary/hybrid baselines | D12 |
| 9 | Compositional/temporal targets (G4) | D16 |
| 10 | Statistics and figures | D21 |
| 11 | Container and upstream PR prep | D21 |
| 12 | Four-page report | D23 |

Record non-obvious choices in `DECISIONS.md`, unknowns in `RISKS.md`, and never commit waveform artifacts.

Slice 7 currently has deterministic DMA channel harnesses, payload checks,
workload validation, useful-work gating, and provenance. The remaining DMA
work is a coupled memory-copy model and synthesis/evaluation integration before
the Ibex adapter is expanded.
