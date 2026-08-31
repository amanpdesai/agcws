# Decision log

## 2026-08-31 — AES evaluator determinism verified

**Finding.** Two independent evaluations of the 24-block scored AES workload
produced byte-identical VCD and activity artifacts, identical useful work (24
blocks), and identical Sky130 OpenSTA mean power (`0.02118620276451`). The
machine-readable record is `out/aes-determinism-final/determinism.json`.
**Decision.** Treat the current simulator/activity/OpenSTA configuration as
deterministic for calibration and comparative runs; rerun this check after
changing simulator, frontend, synthesis, or activity code.
**Rationale.** The calibration assumes evaluator noise does not determine the
result. Hashing both waveform and extracted activity detects nondeterminism that
a matching scalar power value could hide.
**Rejected.** Checking only the final power scalar; accepting waveform
differences without measuring them.

## 2026-08-30 — Own repo, upstream CHIA as pinned read-only dependency

**Decision.** `agcws/` is standalone; `tools/chia` is pinned and read-only.  
**Pinned commit:** `d78ad77e4ce7b11523bf15a253a258c0f8795673`  
**Rationale.** Keep experiments separate from framework work and make upstream extraction reviewable.  
**Rejected.** Fork-and-branch development inside `ucb-bar/chia`.

## 2026-08-31 — Freeze AES calibration from activity-only inner-loop run

**Decision.** AES ε_s is frozen at 0.05 globally. The prescribed five-seed,
five-target random-search calibration solved 5/25 cells (r=0.20), which is
inside the retain-0.05 band. The activity envelope is 128.726293–130.431250
total transitions per clock edge, and the AES useful-work floor is frozen at
36 blocks from the inclusive 10th percentile of the nine valid records in the
ten-workload corpus.
**Rationale.** Calibration uses the same deterministic activity proxy as the
fast search loop; OpenSTA remains a finalist validation tier. The pre-declared
rule therefore determines ε without per-design or post-hoc tuning.
**Rejected.** OpenSTA per candidate during calibration; changing ε after
inspecting comparative results.
**Consequence.** ε_s=0.05 and the 36-block AES floor are fixed for comparative
runs. Generated calibration summaries remain ignored artifacts and can be
reproduced from the pinned repository state.

## 2026-08-30 — AES first, `axi_dma` second, Ibex third

AES has the shallowest bring-up; DMA tests protocol depth; Ibex has the longest toolchain tail.

## 2026-08-31 — Pin all declared RTL sources as HTTPS submodules

**Decision.** Add `third_party/verilog-axi` at
`516bd5dadc3365b7f9e225d2af8fe0b8d804fe53` and `third_party/ibex` at
`8b8ee086aef72e0833b7f0493d9d33f1e4d3c8e2` as HTTPS submodules.
**Rationale.** The declared three-design study must reproduce against exact RTL
revisions without vendoring third-party trees. HTTPS works in clean containers
and for reviewers without configured GitHub SSH keys.
**Rejected.** Floating branch clones; copying RTL into the project tree.
**Consequence.** Harness bring-up can proceed against immutable source inputs;
RTL updates require a new decision and refreshed measurements.

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

## 2026-08-31 — Freeze AES scalar epsilon at 0.10

**Decision.** AES ε_s is frozen at 0.10 normalized envelope units. The initial
0.05 run solved 0/25 target-seed cells within 20 proposals; the one permitted
0.10 re-evaluation also solved 0/25. No further adjustment is permitted.
**Rationale.** This follows the preregistered rule without per-design or
post-hoc difficulty fitting.
**Rejected.** Additional loosening, per-target retuning, or dropping unsolved
cells.
**Consequence.** Unsolved runs remain right-censored at the budget; ε=0.10 is
used for subsequent comparative runs, with 0.02 and 0.05 as sensitivities.

## 2026-08-31 — Superseded: freeze AES useful-work floor at 21 blocks

**Decision.** Scored AES workloads must complete at least 21 blocks, the floor
of the inclusive 10th percentile of the 10-valid-workload calibration corpus.
**Rationale.** The hard floor prevents low-power results from being idle
solutions while remaining grounded in observed workload support.
**Rejected.** A zero-work threshold or selecting the floor after comparison.

**Superseded by the activity-calibration decision above.**
**Consequence.** The 16-block workload remains a harness test, not a scored
experiment workload.

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

## 2026-08-31 — Sky130 HD primary Liberty; Nangate45 cross-check

**Decision.** Use the copied Sky130 HD TT Liberty as the primary validation
library and copied Nangate45 typical Liberty as an independent cross-check.
**Evidence.** Sky130 contains 2,477 `internal_power` groups, 2,477 rise-power
tables, 2,477 fall-power tables, 428 leakage entries, 1,328 capacitance entries,
and 6 clock-gating declarations. Nangate45 contains 2,459, 2,459, 2,459, 126,
404, and 8 respectively. SHA-256 digests are recorded in
`third_party/liberty/README.md`.
**Rationale.** The characterized tables support relative synthesis-level power
analysis; the second library tests whether finalist ordering is robust to
library choice.
**Rejected.** Treating RTL toggles as the final power claim or relying on host
`/opt/eda` paths.
**Consequence.** Reports distinguish per-cycle toggle activity from OpenSTA
synthesis-level power and include cross-library rank agreement.

## 2026-08-31 — Initial cross-PDK result treated as a diagnostic

**Finding.** The four-workload AES temporal corpus produced opposite mean-power
ordering under the two libraries (`Spearman rho = -1.0`). Sky130 and Nangate45
therefore cannot be treated as interchangeable absolute or ranking oracles from
this sample.
**Decision.** Preserve both results, report the disagreement, and expand the
corpus before making any cross-PDK robustness claim. Per-cycle toggle activity
remains the library-independent temporal signal; OpenSTA power remains a
library-specific validation measurement.
**Rejected.** Selecting whichever PDK agrees with the desired narrative or
silently pooling the two power scales.
**Consequence.** Cross-PDK rank agreement is a reported diagnostic and not an
assumed success criterion; the experiment must distinguish activity-profile
agreement from mapped-power agreement.

## 2026-08-31 — Cross-PDK agreement is reported by corpus class

**Finding.** The identical 10-workload AES random corpus (seed 17) produced
`Spearman rho = 1.0` between Sky130 and Nangate45 mean-power ordering, while
the four-workload temporal schedule corpus produced `rho = -1.0`.
**Decision.** Report corpus-class-specific agreement and retain both datasets.
Do not average the coefficients or present the random-corpus result as proof
that temporal profile rankings transfer across libraries.
**Rationale.** Random workloads and hand-shaped temporal schedules probe
different operating regimes; their disagreement is scientifically meaningful.
**Consequence.** Future claims require larger, preregistered corpora and must
separate activity-shape agreement from mapped-power rank agreement.
