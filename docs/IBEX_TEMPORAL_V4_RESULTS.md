# Ibex v4: grounded temporal development

Status: the frozen 48-cell temporal panel is running. This document does not yet
report temporal performance. Earlier studies and held-out results are unchanged.

## Question and intervention

Can a clearer response contract, executed operand/phase diagnostics, and explicit
prediction-to-outcome feedback improve the programmable-Ibex temporal controller?
The model, four observed target profiles, seeds 600–602, legal program language,
16-slot budget, two shared initial programs and 200,000-cycle window are fixed.
This is development on previously observed cases, not held-out confirmation.

Stage A compares the original response contract with a bare-program contract and
native schema generation on twelve identical historical contexts. Stage B compares
random, behavior-coverage, fixed-contract base agent and fixed-contract grounded
agent. The latter adds measured execution feedback and a six-record notebook.
Both agents declare reference-linked eight-bin direction predictions before
execution. Invalid or missing programs still consume requested slots.

The packages are not component ablations: Stage A changes wording and constrained
generation together; Stage B adds diagnostics, notebook and instructions together.
No new RTL-reading ability, reasoning model or autonomous tool-selection policy is
being tested. The runner executes the same compiler and simulator for all arms.

## Response-contract results

| Fixed-context comparison | Original valid programs | Revised valid programs | Outcome |
|---|---:|---:|---|
| Full native schema | 14/24 | 0/24 | All twelve constrained requests rejected by the serving API as too complex |
| Simplified serving schema | 16/24 | 23/24 | Readiness threshold passed; one nine-operation body rejected by the unchanged local validator |

The first failed gate remains archived. Its twelve failed calls have unknown
usage, not verified zero billing. The explicitly versioned second gate relaxes
the server grammar only; local numeric, operation and cardinality rules remain
authoritative. All 24 second-gate calls finished with STOP and known usage.
Estimated cost: $0.1139308 original and $0.118557 constrained.

A separate, frozen one-call prediction-envelope preflight returned two valid
programs and two valid reference-linked predictions ($0.0142723). This is interface
readiness, not evidence of good predictions or temporal search.

## Measurement and attribution

Two real-CPU equivalence checks cover partial body iterations and allocations
shorter than a body. Original and instrumented loadable binaries, expected state,
measurement markers and window transition counts match exactly. Instrumentation
adds assembly labels, not executable instructions.

The new diagnostic distinguishes zero numerator from zero divisor using executed
register operands. It separates segment setup, release polling, body retirement
and final waiting. Phase bounds are first/last retirement times: they do not
identify issue times, stalls or causal power contributions.

The notebook retains declared changes, actual program diffs, predicted directions
and observed deltas, including failures. Directions use an inclusive ±0.01 neutral
band in the fixed normalization. Direction agreement must be reported with its
scorable denominator and missingness. An always-no-change diagnostic baseline is
an additional post-hoc descriptive check, not a replacement primary endpoint.

## Temporal results and trajectories

Pending completion and archive audit. Read proposal-indexed best-so-far AUC first,
then solve counts by target, generated validity, per-run behavior coverage,
prediction agreement, actual edit scope and cost. Inspect all development-seed
finalists rather than choosing attractive examples. No statistical superiority,
new language expressiveness, causal understanding or gate-power claim follows
from a favorable development mean.

## Evidence

- [Frozen development protocol](IBEX_TEMPORAL_V4_PLAN.md)
- [Explicit serving-schema revision](IBEX_CONTRACT_V4_REVISION2.md)
- [Prediction preflight protocol](IBEX_V4_PREDICTION_GATE.md)
- [Failed contract gate](../results/ibex_temporal_v4_contract/)
- [Revised contract gate](../results/ibex_temporal_v4_contract_v2/)
- [Temporal manifest](../results/ibex_temporal_v4_development/manifest.json)

Fresh held-out target families and seeds remain reserved. The recommendation after
this panel must follow its outcomes; improvement is not a condition for extending
the run or revising an evaluated controller.
