# Ibex shared-allocation diagnostic — complete

2026-09-07. Development only; source/prompt/configuration frozen at `1eb5106`
before model calls. All 36 cells and 576 proposal slots completed.
[Protocol](IBEX_PROPOSAL_V2_DEVELOPMENT.md) ·
[Tracked evidence](../results/ibex_proposal_v2_development/) ·
[All finalists](../results/ibex_proposal_v2_development/finalists.svg).

## Primary question: proposal readiness

The shared weighted allocator passes the predeclared readiness gate. Of 168
model-generated slots, **157 are valid (93.45%)**, above the 80% threshold.
There are zero work-count rejections and zero architectural failures. In the
preserved v1 pilot, model-generated validity was 63/168 (37.5%), with 95
work-count rejections. Shared initialization is excluded from both fractions.

All policies use the same allocator, legal language, fixed 4,096 semantic
operations and 200,000-cycle observation. Validity was not purchased by dropping
work, padding with no-ops, lengthening the window or repairing only agent output.
All **192 random-policy slots** reproduce their v1 programs, validity and activity
measurements exactly under the new representation.

## Secondary question: temporal targeting

Lower AUC is better. The observation and normalization are unchanged from v1.

| Policy | Mean AUC | Mean final error | Solved cells | Valid slots |
|---|---:|---:|---:|---:|
| Random | 4.831839 | 0.274697 | 3/12 | 176/192 |
| Mutation with restarts | 5.126319 | 0.281019 | 4/12 | 177/192 |
| Agent | 4.554168 | 0.268424 | 3/12 | 177/192 |

Agent mean AUC is descriptively 5.75% lower than random. This is a useful
development signal, **not evidence of held-out superiority or equivalence**:
there are only three seeds, and the four target profiles were already observed
in v1. No confirmatory significance test is claimed.

All agent and random solves are on `target_1`, the near-flat control. No policy
solves `target_0` or `target_2`; mutation alone solves one `target_3` cell.
The agent has lower mean AUC on targets 0–2 and higher AUC on target 3.
Better aggregate AUC does not demonstrate mastery of the difficult waveforms.

The agent's exploratory grid count is 136 versus random's 44, but random reuses
the same seed stream across targets while the agent is target-conditioned.
These global counts are not a matched-sample expressiveness comparison. The
language is shared; source complexity is not an expressiveness result.

## Failures, cost and evidence

- Eleven model-generated slots fail schema validation: eight nonempty candidates
  omit `registers`, two exceed the eight-operation body cap, and one requested
  candidate is missing. Its slot is charged; the short batch is not discarded.
- All 84 model responses finish with `STOP`; no parse, transport or truncation
  failures are recorded. The four agent useful-work rejections in the full ledger
  all come from shared initialization, not model-generated proposals.
- Recorded usage: 570,208 input and 219,741 output tokens including thinking;
  estimated cost **$0.7204149**, with zero unknown-usage batches. Same Flash model,
  temperature, thinking budget and feedback depth as v1.
- There are 312 unique simulated programs, 304 with valid activity profiles.
  Median recorded evaluation time is 29.91 seconds. Cache hits still consume
  proposal slots; failures remain in AUC and unsolved runs are censored at 16.
- The archive contains raw responses, every ledger/summary, emitted assembly,
  architectural output, frozen source hashes and all finalists. Waveforms remain
  local, compressed as FST. The compact audit checks arithmetic and provenance;
  it does not claim to independently rerun simulation.

Numeric edge case found during review: JSON Schema accepts integral floats such
as `1.0`, while the allocator expects Python integers. No recorded model slot
uses that encoding. Keep v2 frozen; a subsequent interface version must reconcile
numeric handling for every policy and test it before further runs.

## Research decision

The representation is ready for **further controlled development**, after that
numeric hardening—not for a held-out superiority claim. The correction removed a
large avoidable failure mode and yielded an encouraging targeting signal without
a stronger model or extra proposals. It does not isolate which part of the new
representation/prompt caused the change; mutation's weight operator also changed.

Next, test source-grounded context and measured corrective feedback separately,
then an exploration archive against a genuine behavior-coverage-guided baseline.
Use temporal target coverage/error, not program length, as the outcome. Select on
development data, then freeze before fresh target families and held-out seeds.
See [the staged plan](AGENT_CONTEXT_AND_CORRECTION.md).

These are **RTL activity profiles, not gate-level power profiles**. Neither this
diagnostic nor the source-reader scaffold changes the earlier AES/DMA findings.
