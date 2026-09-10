# SAGA-inspired temporal screening v1

2026-09-10. CPU-only integration protocol, frozen before execution. Not a
SAGA reproduction, a model comparison, or baseline hyperparameter selection.

## Upstream diagnostic versus new algorithm

The pinned `PredictReferenceFeatures.py` fits instruction-type counts as
functions of positive measured fitness and extrapolates at max(fitness)+100.
Its actual predictor is exercised separately on a known logarithmic synthetic
function, then on negative fitness. Record returned values and warnings, not
assumed behavior. The isolated probe pins NumPy 2.4.2 and SciPy 1.17.1 through
`uv run --isolated --no-project`; it does not change the project environment.
The source hash and runtime versions are archived. No remote hardware code runs.

Our new named arm is **temporal-ridge-screen-v1**, inspired by surrogate-assisted
search but not using SAGA's original predictor. Exact GeST tournament/crossover/
replacement operators and the declared phase genotype come from the qualified
GeST bridge. The changes are substantive and must remain visible in the paper.

## Features and predictor

Fixed positional features encode eight possible phases: active mask, release
deadline / horizon, allocated work / 4096, body length, preceding work fraction,
instruction mix and simple operand alias fractions. Inactive phases are zero
padded with a distinct mask. Global inputs include phase count, memory seed,
register values, register popcount and zero indicators. This captures phase
order but is not a complete encoding of instruction order or dependencies.
Release deadlines are not actual phase boundaries; no RTL timing is inferred
from them as ground truth. No simulation or witness program is used to compute
candidate features.

Fit centered multi-output ridge regression to eight measured activity rates
divided by the frozen scale. Alpha=1, deterministic dual linear solve. Train
only on earlier valid measured programs, deduplicated by canonical program
(first observation retained). At least two distinct valid programs are required.
No automatic alpha tuning, target leakage, predicted-label training, feature
standardization fitted on candidates, clipping or substitute model on failure.
Prediction failure stops and records charged pending proposals. Negative finite
predictions remain predictions, never valid measured power.

## Frozen smoke

- One existing achieved target: index zero of temporal-scaling v1 targets.
- Seed 850; twelve generated proposals; three batches of four.
- First four random programs are all evaluated and charged.
- Next batches use only earlier measured valid parents (top eight, tournament
  two), produce two GeST offspring pairs, and charge all four candidates.
- Select the lowest predicted target error plus the remaining candidate with
  greatest minimum feature distance to training data. Index breaks ties.
- Evaluate only those two. Other slots are `FILTERED`, with validity, rates
  and measured loss unknown/null. They remain in the proposal-counted ledger.
- Selected invalid candidates consume slots and receive no score or parent role.
  Duplicates count, and cached measurements are distinguished from simulations.

Thus twelve proposals authorize eight selected evaluations, not twelve free
screening candidates plus a hidden budget of eight. Every predicted profile,
predicted error, training slot, distance and pre-measurement selection is logged.
No score for filtered candidates enters the measured best-so-far curve. A future
study may report equal-simulator-call performance separately; this smoke does
not establish savings at equal quality because rejected outcomes are unmeasured.

Use unchanged Ibex 200k-cycle/eight-bin measurement, work checks and disposable
containers. Freeze source, runtime, witness and numerical-dependency identities
before calls. Retain all checkpoints; reconstruct proposal generation and
selection on resume and offline audit. Failed bootstrap is an incomplete
qualification, not permission to replace programs until the test passes.

## Acceptance and next gate

Pass: twelve slots accounted, actual post-bootstrap surrogate screening and
selected CPU evaluation, strict separation of predictions and measurements,
independently audited compact evidence. No held-out seeds or paid calls.
Next, use a separate balanced development target bank to compare original
random, phase-random, phase-GA, GeST adaptation and temporal-ridge screening.
Include a matched no-screening control and assess filtered candidates only in
a separately charged diagnostic tier. Do not select a baseline using the
unchanged fresh-seed Pro confirmation outcomes.
