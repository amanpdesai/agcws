# Plan

Next active direction (2026-09-10): [official baseline integration and temporal
confirmation](UPSTREAM_BASELINES_PLAN.md). First qualify pinned GeST/GeST-SAGA
components against our interface, CPU only. Keep fresh-seed Pro confirmation
separate and unchanged; then develop a balanced witnessed target bank and
stronger-baseline comparison before expanding measurement duration/resolution.
The [upstream component audit](UPSTREAM_BASELINES_AUDIT.md) records pinned sources,
tested interfaces and the remaining ask/tell bridge work; no upstream comparative
run or fresh-seed confirmation has been launched by that qualification.
The next slice implements the [GeST phase bridge](GEST_BRIDGE_V1.md): exact
pinned upstream operators in a bounded ask/tell wrapper, with a declared phase
encoding and an eight-slot CPU qualification. This is an adaptation, not the
full upstream runner or SAGA. See its tracked `results/gest_bridge_v1` evidence
for completion; the fresh-seed Pro study remains separate.
The [eight-slot bridge qualification](../results/gest_bridge_v1/README.md) is
complete: seven valid, one useful-work failure, six upstream-operated slots,
zero model calls. Next: qualify SAGA's temporal adaptation and the balanced
development panel; do not present this smoke as a stronger-baseline result.
The [temporal surrogate qualification](../results/saga_temporal_v1/README.md)
is now complete: twelve charged proposals, eight valid selected simulations and
four unmeasured filtered candidates. The actual upstream predictor was exercised
separately; temporal screening uses a clearly labeled ridge adaptation. Next is
a matched stronger-baseline development panel, not another efficacy claim from
a single smoke. Frozen Pro confirmation is still separate and unlaunched.

Current research extension: [staged hypothesis roadmap](RESEARCH_DIRECTIONS.md)
and [model × reasoning fixed-context probe](IBEX_CAPABILITY_V1_PROTOCOL.md).
These are new development stages; prior frozen studies are not being amended.
The capability probe is [complete](IBEX_CAPABILITY_V1_RESULTS.md): Pro-4096
passes the predeclared development screen. The [closed-loop depth
comparison](IBEX_DEPTH_V1_RESULTS.md) is complete: 48 trajectories,
6,144 slots, four policies and 16/64/128 prefix summaries. Pro improves over
both controls in development; fresh held-out confirmation remains future work.

Next scoped milestone: [temporal scaling and stronger-control qualification](TEMPORAL_SCALING_V1_PLAN.md).
Build deterministic request generation and witness checks; qualify phase-random
and phase-GA on the unchanged Ibex evaluator using CPU only. Fresh-seed Pro/random
confirmation is the next paid study and must keep the completed protocol fixed.
New horizons, bin counts, stronger-baseline comparisons and new-family claims
have separate implementation and freeze gates, not a silently enlarged matrix.
The [first CPU qualification](TEMPORAL_SCALING_V1_RESULTS.md) is complete:
84 total slots, zero model calls. Synthetic requests are not yet qualified;
only measured witness-derived targets are feasible evidence.

The post-results [research assessment](RESEARCH_DIRECTION.md) separates
demonstrated waveform feasibility from unproven agent superiority and proposes
a fresh complexity-controlled extension. It does not amend either frozen study.
The [retention record](../results/artifact_retention_20260906.json) documents
verified compression, exact-path cleanup and the permission-blocked remainder.

## Current research checkpoint — 2026-09-06

The versioned semantic-search development and frozen AES/DMA evaluation are
complete: 550 held-out cells, all five targets, ten seeds and 50 proposal
slots per cell. Original manifests, ledgers, complete-panel inference and
cost-uncertainty flags are tracked. See [SEMANTIC_RESULTS.md](SEMANTIC_RESULTS.md).
This supersedes historical notes below saying Vertex credentials or
multi-design scalar agent runs are still missing. It does not complete the
whole project. The structural temporal milestone is now also complete:
160 frozen cells / 5120 slots, two designs, four methods, ten fresh seeds,
and 16 matched-window GLS finalists. See [STRUCTURAL_RESULTS.md](STRUCTURAL_RESULTS.md).
No agent advantage over random is established. Native eight-window gate-power
validation is complete for all sixteen finalists and four achieved references
(180 reports); see [WINDOWED_POWER_RESULTS.md](WINDOWED_POWER_RESULTS.md).
A [four-page working draft](../paper/report.pdf) now integrates both frozen
studies and the windowed measurements. Venue formatting, author review, a
upstream submission, and a full clean-checkout synthesis check remain. Two
image-only AES/DMA gate/window replays passed on 2026-09-07; see the
[compact evidence](../results/container_window_replay_v1/README.md). Compositional
held-out evaluation is not part of these completed results. The broad slice
table below tracks the original project, not just these two-design milestones.

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
| 12 | Four-page report draft complete; author/venue review pending | D23 | WIP |

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
runner, with both Ibex FuseSoC source closures fingerprinted. The five-policy,
five-seed DMA comparative matrix and paired inference are complete; the widened
experiment still requires the full multi-design/profile factorial study and
full Ibex synthesis/power integration. The full 91-source Ibex closure now passes
Verilator lint in the reproducible container. The standalone
`lowrisc:ibex:ibex_core` Slang/Yosys frontend probe now
elaborates successfully from an isolated artifact root. Memory inventory is
also reproducible, but the current asynchronous read memories fall back to
FFs; no BSG macro-mapped Ibex netlist is claimed. The default
`lowrisc:ibex:ibex_simple_system` wrapper now runs through functional simulation
and RTL activity extraction in the verification container. Its
wrapper-to-mapped-netlist/OpenSTA path remains unsupported; no Ibex gate-level
power result is treated as valid until synthesis and mapping are completed for
that selected closure.
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

Latest verification checkpoint (2026-09-01): `make verify` passes with 201
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

## Memory-aware synthesis track

The first implementation pass inventories inferred Yosys memories before
`memory_map` and emits contract-only macro collateral. The synthesis policy is
per-memory: compatible geometries are mapped to the characterized
bsg_fakeram-compatible backend; incompatible memories are deliberately left
for ordinary flop/distributed mapping. `AGCWS_MEMORY_MANIFEST` records the
eligible and flattened counts and the scripts reject manifests without this
explicit policy. This keeps the large compatible majority on macros without
silently claiming that unsupported port semantics were mapped, and records
both collateral digests.
The all-design audit (`make audit-memory-collateral-all`) passes for the
regenerated AES, AXI DMA, and Ibex bundles. Their `mapping_ready: false`
statuses are intentional: AES has no memories, while AXI DMA and Ibex require
memory interfaces not provided by the pinned synchronous 1RW BSG backend.
The current reproducible scalar analysis was regenerated from
`out/aes-baseline-matrix-complete` into `out/final-analysis/`, producing 25
policy-target records and `convergence.png`; this remains AES-only evidence.

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
