# Programmable CPU temporal pilot — development result

Completed 2026-09-07. **36 cells, 576 proposed slots, all outcomes archived.**
This is a separate exploratory study, not a replacement for the frozen AES/DMA
results and not a held-out superiority claim.

## Primary result

Random has the lowest mean proposal-counted target-error AUC. The full-program
agent does not improve average targeting over random on this panel.

| Policy | Mean AUC ↓ | Mean final error ↓ | Solved runs | Valid slots |
|---|---:|---:|---:|---:|
| Random | 4.8318 | 0.2747 | 3/12 | 176/192 |
| Mutation + restarts | 5.6622 | 0.3405 | 2/12 | 179/192 |
| Feedback agent | 5.5126 | 0.3402 | 2/12 | 83/192 |

AUC integrates indices 1–16 with the predeclared best-error cap of 1. All
sixteen slots are retained even after solving. Unsolved runs are right-censored
at sixteen, not dropped. Mean censored proposals-to-target are 13.00, 14.75 and
14.25 respectively; these are descriptive capped values, not estimates of an
uncensored completion-time mean. There are only three development seeds, so no
significance, equivalence or cross-design generalization claim is made.

| Anonymous target | Random AUC | Mutation AUC | Agent AUC | Solves: random / mutation / agent |
|---|---:|---:|---:|---|
| target_0 | 8.4273 | 8.5838 | 8.7155 | 0 / 0 / 0 |
| target_1 | 1.1886 | 2.5082 | 1.6444 | 3 / 1 / 2 |
| target_2 | 5.8974 | 6.5761 | 6.8045 | 0 / 0 / 0 |
| target_3 | 3.8141 | 4.9809 | 4.8861 | 0 / 1 / 0 |

Mutation alone solves one non-flat target instance, but that does not reverse
the primary aggregate ordering. Random and agent each solve one target family
in at least one seed; mutation solves two. These are four researcher-selected
achieved profiles, not a representative estimate of the whole CPU envelope.

## What the implementation establishes

Ibex now supports genuine bounded instruction loops, programmable operands and
register dependencies, multiply/divide, memory aliases and conditional control
flow. All policies can construct the same programs. The agent emits complete
programs rather than only scalar edits and receives seven feedback rounds after
two shared initialization proposals. Its context contains the full schema,
instruction semantics, target vector and compact successes/failures.

The pinned CPU is RV32IM with a fast multiplier, no instruction cache and local
RAM. This is a more programmable interface than AES, not a representative sample
of all hardware or an out-of-order/cache-concurrency experiment.

Four independently authored witness profiles span 226.16–754.61 core bit changes
per edge across their bins. The gate exercises every operation, independently
checks all eight registers and all 64 memory words, and reproduces the measured
bit counts exactly. Targets were not drawn from the baseline sampler and their
programs were not supplied to the agent. A near-flat target is an intentional
control; the others contain different low-activity regions.

Every valid candidate performs exactly 4,096 semantic body operations inside a
fixed 200,000-cycle, eight-bin observation. Reset, initialization and printing
are outside the window. Waiting is active CSR/branch polling, not sleep. Activity
is unique core-net **bit** transitions, excluding the clock and CSR-register
subtree; signal copies outside that subtree can still contribute. It is not the
older bus-change metric, whole-system energy, or gate-level power. Retired
instruction metadata counts the full trace, including surrounding harness code.

The language demonstrably admits distinct profiles. **The agent has not shown
greater effective profile coverage under this budget**, and shared-language
coverage is not intrinsic language expressiveness.

## The dominant failure is benchmark resource accounting

| Agent rejection stage | Slots | Finding |
|---|---:|---|
| SCHEMA | 8 | Oversized bodies, out-of-range integers or an extra operand |
| PROTOCOL | 95 | `sum(iterations × body_length)` was not exactly 4,096 |
| FUNCTIONAL | 0 | No scored candidate failed the architectural reference |
| USEFUL_WORK | 6 | Work did not fit the declared observation window |

Here `PROTOCOL` is the existing static-stage label: these 95 failures violate
the benchmark's work-conservation rule, not an ISA or bus protocol. The 83 valid
slots include 20 valid shared-initialization slots. Of the **168 model-generated
slots, 63 were valid (37.5%)**. Four of the six useful-work rejections were also
shared initialization. The model therefore received substantially fewer scored
search attempts than the nominal sixteen-slot budget, as the fairness rule
requires.

All 84 Vertex calls reported `FinishReason.STOP`; none failed JSON parsing or
required a free repair. These are not truncation/quota failures. The eight schema
rejections are well-formed JSON that violates the typed schema. Zero functional
failures after earlier filters is not proof of general hardware reasoning.

This does not isolate the cause of poor target search: resource-compliance and
profile reasoning remain coupled. Do not conclude that CPUs are unsuitable,
that larger models cannot help, or that agents inherently cannot synthesize
useful instruction sequences.

## Evidence and cost

- [Frozen protocol](IBEX_EXPRESSIVENESS_DEVELOPMENT.md), committed before comparison.
- [Archive](../results/ibex_temporal_development_v1/README.md): all per-run summaries,
  full proposal ledgers, raw model responses, target witnesses, evaluator records,
  emitted assembly, architectural outputs and frozen sources.
- [All-seed finalist figure](../results/ibex_temporal_development_v1/finalists.svg):
  all 36 within-budget finalists, not selected winning examples.
- 222 unique search simulations, with shared caching available to every policy:
  213 valid profiles and nine unique observation-window rejections. Repeated
  proposals and cache hits still consume slots. Feasibility runs are separate.
- Gemini `gemini-2.5-flash`: 475,552 input and 177,530 output tokens including
  thinking; **$0.58649 estimated**, zero unknown-usage batches. No billing-export claim.
- Median unique evaluation runtime about 30 seconds under variable concurrency.
  Runtime includes execution and extraction; it is not a controlled speed ranking.
- The archive verifier reconciles all 36 cells and 576 slots, including source,
  witness and content-cache hashes, actual architectural outputs, AUC, censoring
  and token/cost accounting. It does not independently rerun simulation.

The archive's grid-diversity counts are exploratory descriptors, sensitive to
grid width and repeated seeds across targets. In particular, random reuses its
same seeded stream across target runs. Do not use the union counts as evidence
of intrinsic expressiveness or an independent-sample superiority test.

## Recommendation

**Do not launch a confirmatory study of this controller unchanged.** Preserve
this entire pilot and the earlier AES/DMA studies. The immediate development
problem is that the interface forces the model to conserve a global operation
count by arithmetic while the baseline constructors enforce it by construction.
That is a real end-to-end disadvantage, but a poor isolation of the proposed
hardware-semantic advantage.

A defensible next development version would expose a common, deterministic
work-allocation representation or helper to **every** policy, retaining real
instruction dependencies and the hard fixed-work/window gates. It must not
silently repair only agent proposals or rewrite these results. Test whether
validity improves before spending on a larger study. Model/depth probes can then
be development-only comparisons, not retroactive changes to this panel.

For a later confirmatory study, select fresh target families as well as fresh
seeds, including data-dependent-latency and dependency/alias patterns at matched
pacing, and retain strong family-aware random and mutation baselines. Add an
actual coverage-guided baseline before making any claim against coverage-guided
fuzzing. Freeze representation, controller, targets, budgets and analysis anew.
Ibex gate-power validation is a separate prerequisite for a power-level claim.

The substantive step here is a checked programmable-CPU testbed and a complete
diagnostic comparison. It is **not** the positive agent result we hoped to find.
