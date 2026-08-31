# Decision log

## 2026-08-30 — Own repo, upstream CHIA as pinned read-only dependency

**Decision.** `agcws/` is standalone; `tools/chia` is pinned and read-only.  
**Pinned commit:** `d78ad77e4ce7b11523bf15a253a258c0f8795673`  
**Rationale.** Keep experiments separate from framework work and make upstream extraction reviewable.  
**Rejected.** Fork-and-branch development inside `ucb-bar/chia`.

## 2026-08-30 — AES first, `axi_dma` second, Ibex third

AES has the shallowest bring-up; DMA tests protocol depth; Ibex has the longest toolchain tail.

## 2026-08-30 — Local compute, credits reserved for LLM

Simulation/synthesis/STA run locally; GCP credit is reserved for Vertex AI.

## 2026-08-30 — Non-LLM search before the agent

Close the loop with hill-climbing first to establish a fair harness and fallback result.

## 2026-08-31 — OpenTitan AES as the first real design dependency

**Decision.** Use the HTTPS-pinned `third_party/opentitan` submodule at commit
`b16f2be75d2f38c62d861208453ed5b81ccf41b0`; use its TileLink-connected `aes`
top level for the production adapter.  
**Rationale.** It is an established, self-contained crypto IP with meaningful
internal hierarchy and legal register/data workload semantics.  
**Rejected.** Driving only `aes_cipher_core` as the headline interface; it
would simplify bring-up but would not represent a realistic legal workload.  
**Consequence.** The first harness must provide deterministic TileLink,
entropy, lifecycle, key-manager, and alert plumbing.

## 2026-08-30 — Proposal-counted evaluator budgets

**Decision.** N=200 for scalar and N=300 for profile goals; every proposed candidate consumes budget, including malformed and rejected candidates. Simulations are secondary.  
**Rationale.** Prevents free LLM retries and makes validity visible.  
**Rejected.** Counting only simulated candidates; wall-clock equalization.  
**Consequence.** N remains provisional until Slice 4 runtime calibration.

## 2026-08-30 — Pre-declared tolerance calibration

**Decision.** ε_s=0.05, ε_c=0.05, ε_t=0.10, with at most one AES-derived global scalar adjustment using the rule in `EXPERIMENTS.md`.  
**Rationale.** Avoids per-design post-hoc difficulty fitting.  
**Rejected.** Absolute-watt or per-design tolerances; dropping unsolved runs.

## 2026-08-30 — Four-stage validity gate

**Decision.** SCHEMA → PROTOCOL → FUNCTIONAL → USEFUL WORK; invalid workloads receive no score and useful-work floors are hard gates.  
**Rationale.** Prevents simulator undefined behavior and idle solutions from winning.  
**Consequence.** Floors are provisional until Slice 4 and then frozen here.

## 2026-08-30 — Generic frozen agent prompt

**Decision.** Flash for scalar, Pro for profile goals; one design-agnostic prompt frozen after Slice 6 with a recorded hash.  
**Rationale.** Preserves the cross-interface generality claim and makes prompt changes auditable.  
**Rejected.** Per-design prompt tuning and silent model substitution.
