# Ibex proposal interface v2 — development protocol

Declared 2026-09-07 before new model calls. Preserve v1 and its frozen sources.
This addresses avoidable work-allocation failures, not held-out superiority.

## Representation

Segments supply positive integer weights instead of iterations. Assign exactly
4,096 operations proportionally using integer Hamilton allocation, index tie
breaks, then a one-operation minimum: transfer from the largest allocation to
any zero allocation, again breaking ties by index. Execute whole loop iterations
and then the required body prefix. These are public language semantics shared
by every policy, not an agent-only repair.

Keep body lengths 1–8, all operations, dependencies, memory effects and release
timing. No no-op padding or discarded segments. Out-of-schema proposals remain
rejected and charged. Every valid v1 program embeds exactly by choosing its
per-segment operation counts as weights; its assembly must remain byte-identical.

## Gate before comparison

- Property tests: exact total, positive allocations, tie handling, extreme
  ratios, invalid-weight rejection and exact v1 embedding.
- CPU checks: partial iterations, allocations smaller than a body, conditional
  control, memory effects, all eight registers and all 64 memory words.
- Replay an embedded v1 witness and require identical measured bins.
- Preserve the hard 200,000-cycle observation and completion gate.

## Bounded comparison

Reuse the four v1 development targets and seeds 600–602 as explicitly observed
development data. Sixteen requested slots, two shared initial proposals, batches
of two, random/mutation/full-program agent. Same Flash model and sampling settings;
no model-size or retry-policy change. Freeze sources and prompts in a new manifest
before model calls.

Primary diagnostic: validity of the 168 model-generated slots, excluding shared
initialization. Readiness criterion: at least 80% fully valid, zero work-count
rejections, and no architectural mismatches. Report schema and observation-window
rejections separately. No free reprompts, uncharged simulations or retrospective
repair of v1 outcomes. Preserve failures if the criterion is missed.

Secondary: AUC, solves and right-censoring at the unchanged targets and tolerance.
Compare policies within v2. Mutation can now change weights, so cross-version
mutation differences are not a pure representation ablation. Agent v1/v2
differences are development evidence, not held-out evidence or semantic causation.

Only then consider fresh target families and a held-out protocol. Do not silently
keep tuning this comparison to obtain a favorable result.
