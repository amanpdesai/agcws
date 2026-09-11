# Plan

Updated 2026-09-11. Findings and completion status live only in
[RESULTS.md](../RESULTS.md); compact evidence lives in `results/`.

## Where we stand

The consolidation milestone is complete at `72a8bc663`: one maintained study
pipeline, a verified historical source archive, published compact evidence and
documented scratch retention. Verification is recorded in
[archive/verification.json](../archive/verification.json).

The scientific evidence supports a scoped Pro-versus-phase-random finding on
one Ibex target-construction family. It does not yet establish the mechanism,
superiority to a well-tested evolutionary baseline, arbitrary temporal-profile
generalization or Ibex gate-power accuracy. Earlier frozen negative studies
remain part of the paper. Differences in design, model, budget and task prevent
attributing their contrast to interface expressiveness alone.

## Next milestone: try to falsify the result

The objective is not to make the agent win more. Seek evaluator errors,
information asymmetries and comparison-design weaknesses that could explain
the observed advantage. A large effect motivates scrutiny, but is not itself
evidence of a confound. Audit consistency and scientific validity separately.

The steps below are planned, not executed or pre-registered by this document.
Freeze the inspection selection before opening solutions; freeze any extension
protocol before evaluation. Do not launch jobs merely by following a status
page. New measurements and paid calls require an explicit execution decision.

| Order | Work | Status | Exit condition |
|---|---|---|---|
| 1 | Inspect solutions and measurement behavior | WIP | Explain representative successes and identify any disqualifying behavior |
| 2 | Audit information access and accounting independently | TODO | Reconcile raw records and classify information overlap |
| 3 | Phase-GA robustness extension at 128 slots | PLANNED — NOT LAUNCHED | Compare an untuned, matched-budget evolutionary control |
| 4 | Qualify a more diverse target bank | PLANNED — NOT LAUNCHED | Freeze construction/search rules and retain every attempt |
| 5 | Fresh broader confirmation | CONDITIONAL | Qualified targets, frozen controls and sufficient analysis time |
| Gate | Paper claims | WAITING ON VALIDITY | Audit validity and test competing mechanisms before finalizing claims |

### 1. Solution inspection: cheapest falsification first

Before inspecting programs, record a deterministic selection rule. Cover all
three targets, first-solving and best programs, and representative baseline
solutions and failures. Select by declared seed/slot rules, not by whether the
program looks convincing. Explain ties and cases with no solve. A few examples
can find a failure mode; their absence cannot prove the entire panel is sound.

For each selected trajectory, inspect the exact submitted program alongside:

- Its phase releases, allocated operations, operands, dependencies and memory effects.
- Executed retirement and phase timing, not just the intended schedule.
- Useful-work accounting, including repetitive or ineffective operations that
  pass the counter without supporting a stronger notion of useful computation.
- Requested and achieved activity bins, observation boundaries, reset/wait/tail
  behavior and whether execution finishes in the declared window.
- First-solve versus later-best behavior, so attractive final programs do not
  hide how the tolerance was first reached.

Use retained traces for finer-resolution and shifted-bin diagnostics, with
explicit boundary handling and the same physical observation interval where
possible. These are sensitivity checks, not replacements for the frozen
eight-bin endpoint. Eight-bin matching does not promise sub-bin matching.
Record missing traces and any replay need: cleanup retained best-candidate and
witness waveforms, not necessarily every first-solving waveform. Compressed
execution logs and compact records remain available; do not silently replay.

Classify findings as simulator/evaluator error, legal exploitation of an
underspecified objective, or plausible workload behavior. A legal but vacuous
useful-work solution may narrow the claim even if functional checks pass.
If a defect could invalidate results, pause stronger comparisons and identify
the affected cases before correcting or withdrawing claims.

### 2. Information access and independent accounting

Inspect the frozen, actually sent payloads and original sources, not only the
new runner. Build an information-access comparison for Pro and the controls:
target vectors/scales, schema, hardware semantics, history, diagnostics and
initial programs. Check witness contents, constructor settings, hidden target
metadata, cross-cell history and witness/cache reuse paths. A common cache is
not proof of leakage; verify what information could reach the policy.

Separate three hypotheses:

1. **Actual leakage:** hidden witness programs, constructor parameters or other
   cells' results reached the controller contrary to the protocol.
2. **Unequal information:** target-specific hints or feedback were unavailable
   to the comparison policy despite the claimed fairness contract.
3. **Distribution alignment:** a policy recognizes structure common to the
   constructor's target family. This limits generalization without necessarily
   invalidating the scoped comparison.

Compare prompt/adapter vocabulary with constructor parameters, then trace the
meaning and visibility of overlaps. Grepping is a lead, not a verdict. Shared
phase vocabulary is expected when every policy uses the same phase language;
target-specific template disclosure is a different issue. Out-of-family
testing is needed for a broad claim regardless of a clean literal-leakage audit.

Reconstruct the primary endpoint from raw records using an independently
reviewed calculation, not merely the original summary helper. Reconcile every
requested slot, initialization, malformed/short batch, API failure, duplicate,
cache hit, selected/filtered proposal and valid measurement. Check AUC indexing
and invalid-prefix handling, normalization, right-censoring, seed pairing,
cost/unknown-usage reservations and the exclusion of witness qualification from
search histories. Compare the reconstruction to published aggregates. Preserve
all discrepancies; do not fix records to obtain agreement.

### 3. Stronger-control robustness check

Run phase-GA at 128 proposed slots on the existing confirmation targets and
seeds, with matched initialization, measurement, feedback and accounting.
Inspect the qualified implementation and freeze its exact settings first.
Do not tune it on these now-observed targets. If tuning is necessary, use a
separate development bank and declare the tuning budget.

This is a **post-hoc robustness extension**, not an amendment to the original
held-out confirmation. Keep its outputs separate. Verify evaluator equivalence
before combining new baseline measurements with historical Pro records; the
new runner's unit tests alone do not establish measurement equivalence.
If phase-GA closes the gap, narrow the advantage claim. If it does not, report
the tested control and uncertainty rather than declaring all classical search
defeated. CPU-only means no model-token cost, not zero runtime or compute cost.

### 4. Target diversity before larger hardware

Prioritize independent targets over adding more seeds to the same three targets.
Vary uneven steps, separated bursts, ramps, transition count, dwell lengths and
contrast. Include achieved targets from different program families and
classical-search-generated witnesses. A different constructor is a test of
distribution sensitivity, not automatic proof that all constructor effects are
eliminated. Larger hardware is not the default next step.

For analytic requests, freeze before qualification:

- Family definitions, sampling distribution, seeds and number of attempts.
- Horizon, bin grid, scale, useful-work gate, non-flatness and distance rules.
- Witness-search policies, per-attempt budget, matching tolerance and stopping rules.
- Acceptance/selection order and treatment of failures and duplicate witnesses.

Retain **every** request and qualification attempt, including failures. Distinguish
the analytic request, the achieved witness profile and their distance. Decide
in advance which is the scored target. Failure to find a witness is not proof
of infeasibility; do not quietly substitute an easier waveform. Report the
acceptance rate and resulting selection bias. Qualification must not use Pro's
comparative success to select targets. Witness programs remain hidden from
search unless a separately labeled, equally available reference-edit study is
explicitly declared.

Start with the existing horizon and eight bins to isolate target-family change.
Longer horizons and 16-bin resolution are separate scaling axes requiring their
own feasibility and measurement checks, not simultaneous changes to this panel.

### 5. Fresh confirmation and paper decision

Freeze the controller, qualified target bank, baseline settings, endpoint,
inference and failure handling; declare fresh seeds before comparative runs.
Scope the claim to the qualified distribution. Do not merge incompatible study
regimes or rewrite earlier outcomes. Cross-design Pro addresses generalization;
Ibex gate-power validation addresses the power claim. They are distinct,
conditional extensions, not substitutes for validity checks.

Validity and mechanism evidence gate the paper. The user has explicitly chosen
thorough investigation over rushing the manuscript. Preserve evidence and
methods notes as work proceeds, but do not use writing pressure as a reason to
stop testing alternative explanations. A policy win is not a demonstration
that semantic understanding caused it.

Size extensions from measured runtimes, qualification yield and available
analysis/writing time, not assumed one-day or week-long estimates. Proceed with
the broader confirmation only after steps 1–4 pass their gates and there is time
to finish analysis, not merely launch jobs. If a broader claim remains unsupported,
retain the narrower scope rather than treating a deadline as validation.

The first slice follows the frozen [inspection protocol](SOLUTION_AUDIT.md).
