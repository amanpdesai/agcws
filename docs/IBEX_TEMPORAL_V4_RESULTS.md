# Ibex v4: grounded temporal development

All 48 cells and 768 requested slots completed. Random has the lowest mean AUC;
the grounded package does not improve temporal search. The response interface is
more reliable, but that is not a workload-quality win. Earlier studies and held-out
results are unchanged.

## Primary result

Lower proposal-indexed best-so-far AUC is better. Each arm has twelve cells;
generated validity excludes the two shared initialization slots in each run.
Unsolved runs remain right-censored at sixteen proposals.

| Policy | Mean AUC | Solves / 12 | Generated valid / 168 | Behavior cells per run | Estimated USD |
|---|---:|---:|---:|---:|---:|
| Random | 4.831839 | 3 | 156 | 14.33 | 0 |
| Coverage-guided | 5.123888 | 3 | 153 | 7.42 | 0 |
| Base agent | 4.990451 | 3 | 164 | 8.83 | 0.6927944 |
| Grounded agent | 5.234116 | 3 | 158 | 8.08 | 1.0617662 |

Grounding adds +0.243665 AUC relative to the base agent; both agents have higher
mean AUC than random. These are descriptive development differences, not
significance or equivalence tests. All twelve solves across the four arms are on
near-flat `target_1`. **No policy solves targets 0, 2 or 3.** Random's exact v3
programs, validity, rates and losses reproduce; its comparison settings did not
silently move. Finite-budget behavior coverage is not intrinsic expressiveness.
The v3 base mean (4.566393) was lower than the new base mean. This cross-version
change also introduces structured predictions and revised instructions; it is
not an isolated estimate of constrained decoding's effect on search quality.

| Target | Random AUC | Coverage AUC | Base AUC | Grounded AUC |
|---|---:|---:|---:|---:|
| 0 | 8.427326 | 8.138431 | 7.804649 | 8.596266 |
| 1 | 1.188552 | 1.441535 | 1.283378 | 1.066995 |
| 2 | 5.897396 | 6.356853 | 6.268355 | 6.395374 |
| 3 | 3.814082 | 4.558735 | 4.605422 | 4.877830 |

The grounded agent's favorable near-flat target is not the headline. See
[all 48 finalists](../results/ibex_temporal_v4_development/finalists.svg), including
all three seeds for every policy/target, against the achieved reference profiles.

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

## What the trajectories show

The controller is closed-loop: seven model calls of two candidates per run,
following two shared initial proposals. Both arms see prior measured profiles
and residuals. The grounded arm additionally receives executed phase/operand
diagnostics and the last six prediction/outcome records. No private reasoning
trace is inferred; analysis uses the public hypotheses, programs and predictions.

| Diagnostic | Base | Grounded |
|---|---:|---:|
| Scorable predictions / generated slots | 158/168 | 156/168 |
| Matching predicted bin directions | 481/1264 (38.05%) | 471/1248 (37.74%) |
| Always predict no change, same scorable bins | 349/1264 (27.61%) | 402/1248 (32.21%) |
| All eight directions supported | 1/158 | 1/156 |
| First-position candidates with exactly one scalar-leaf edit / scorable | 3/80 | 6/78 |
| Repeated valid programs within a run | 4 | 7 |

The always-no-change and edit/repetition breakdowns are post-hoc diagnostics,
not new endpoints. Bins are dependent, prediction availability differs, and
agreement does not establish causal understanding. A one-container replacement
in the diff is not counted as one scalar edit. Multi-field changes can be one
conceptual intervention, so this strict count is not a universal focus metric.

Base has four generated useful-work failures and six unscorable metadata records.
Grounded has five useful-work and five schema failures, plus two unscorable
metadata records. Its five schema failures exceed the eight-operation body cap;
they are not the old nested-program envelope failure. There are no protocol or
architectural-functional rejections. First/last-round generated validity is
23/24 → 24/24 base and 21/24 → 24/24 grounded: the v3 late-round schema collapse
does not recur. All failed slots remain charged.

Two concrete checks from the first seed, reviewing the first and last batches
across all four grounded targets:

- `target_0/seed-600`, slot 15 references slot 12 and changes only segment 1's
  release from 10,000 to 5,000 cycles. It predicts increases in the first two
  bins. Measured body retirement moves from cycles 10,001–13,999 to 5,009–9,007,
  but both intervals lie inside bin 1. Later release polling absorbs the saved
  time. Bin 1 changes by only +0.004644 normalized; all other bins are exactly
  unchanged. All eight classify as neutral under the frozen band. Its 6/8
  direction score comes from the six predicted-neutral bins, not successful
  control of the intended increases. “Unchanged” here means within the declared
  neutral band, not byte-identical profiles.
- `target_2/seed-600`, slot 15 references slot 13 and changes both a segment
  weight and release. It predicts `[0,0,0,0,-1,-1,1,1]`; the measured directions
  are `[-1,-1,-1,-1,0,1,-1,-1]`: 0/8 match. Weight normalization reallocates the
  fixed work budget across segments, so an apparently local weight edit is not
  a local timing intervention. The notebook makes this contradiction visible;
  providing it did not make the controller's predictions reliable.

These examples illustrate mechanisms, not a selected winning subset. Every raw
response, exact payload and predicted/observed delta is in the tracked archive.

## Cost, verification and recommendation

The temporal panel made 168 model calls, all STOP, with no unknown usage:
2,517,352 input tokens and 399,742 output tokens including thinking; $1.7545606
estimated. Reported model identifier: `gemini-2.5-flash`. Grounded input use is
1,864,154 versus base 653,198, without better mean AUC or direction agreement.
This does not isolate context length as a cause. The earlier readiness gates
are separate costs, not folded into comparative proposal budgets.

The compact audit reconstructs candidates, emitted assembly, static rejections,
functional reference state, target losses, censoring, costs, exact prompt payloads,
raw response decoding, predictions and v3 random controls. It checks hashes for
all retained evidence, including readiness prerequisites. It is not an independent
simulator or retirement-trace rerun. Large FST/trace scratch is not committed.
The final test run passed 497 tests and lint; an earlier repeat hit an existing
CHIA/Ray startup timeout, then passed on rerun without code changes.

**Recommendation:** retain the response-contract and measurement infrastructure;
do not promote this grounded controller or call it a step forward in temporal
performance. Do not spend fresh held-out data on it unchanged. More diagnostics
have not become actionable temporal control, and the non-flat targets remain
unsolved by every policy, so this is not evidence that the CPU task is trivial.

If another development iteration is chosen, isolate action-to-window reasoning:
a shared tool should summarize actual phase/bin occupancy, requested versus
effective release, and global work reallocation for a reference-based edit.
Test a bounded one-factor intervention path while retaining full-program
exploration, with the same tool and budget available to baselines. First test
whether it improves the accuracy of predicted changes on a fixed development
probe; only then freeze another search comparison. That is a proposed next
experiment, not an implemented feature or a promised win. Do not change the
model, depth, tool package and target family simultaneously.

The current evidence rejects a win for this package in this setting, not the
general possibility of agents producing useful temporal workloads. All policies
share the language; no greater intrinsic expressiveness or power-guided advantage
has been demonstrated.

## Evidence

- [Frozen development protocol](IBEX_TEMPORAL_V4_PLAN.md)
- [Explicit serving-schema revision](IBEX_CONTRACT_V4_REVISION2.md)
- [Prediction preflight protocol](IBEX_V4_PREDICTION_GATE.md)
- [Failed contract gate](../results/ibex_temporal_v4_contract/)
- [Revised contract gate](../results/ibex_temporal_v4_contract_v2/)
- [Temporal manifest](../results/ibex_temporal_v4_development/manifest.json)
- [Complete aggregate](../results/ibex_temporal_v4_development/aggregate.json)

Recompute the archive audit from a checkout with dependencies installed:

```bash
python -m analysis.ibex_temporal_v4 --archive results/ibex_temporal_v4_development
```

Fresh held-out target families and seeds remain reserved. All staged outcomes
are retained; no failed cell was replaced to obtain an improvement.
