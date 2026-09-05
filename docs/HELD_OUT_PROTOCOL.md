# Semantic search held-out protocol

Declared 2026-09-05, before running seeds 200–209.

Development uses seeds 100–199 only. Finish all five targets on AES and DMA
before selecting and recording a controller version. Any later controller,
prompt, schema or evaluator change requires a new version and a new evaluation;
do not combine versions as one method. Selection is documented, not automatic
stopping when a promising cell finishes.

## Fixed evaluation

- AES transaction and DMA pipelined backends, each with its archived calibration.
- Targets 0.10, 0.25, 0.50, 0.75, 0.90; seeds 200–209; 50 proposal slots;
  batch size 4; epsilon 0.02 inherited from the AES calibration rule.
- Random, mutation, evolutionary, scalar-edit-evolution and the frozen semantic
  controller on both designs. Instrumented coverage-guided-line on AES only.
- Invalid, missing and duplicate proposals consume slots. All methods use the
  same validator, useful-work floor, evaluator and feedback availability.
- Primary endpoint is AUC of best-so-far normalized error, lower is better.
  Always report solve rate with right-censored evaluations-to-target (50 for
  unsolved runs), validity by stage, tokens and estimated cost.

## Inference and claim rules

For each design and baseline, pair semantic and baseline AUC at identical
target and seed. Average the five differences within each seed first: ten
seed-level differences, not fifty independent target/seed observations.
Report their mean, deterministic 10,000-replicate paired seed bootstrap 95%
interval (bootstrap seed 0), and exact two-sided sign-flip p-value.
Apply Holm correction jointly across the nine baseline comparisons (four
per design, plus AES coverage). Per-target breakdowns are secondary.

Do not interpret a nonsignificant difference as equivalence or parity. There
is no predeclared equivalence margin: use descriptive language if intervals
include zero. A superiority claim needs a lower agent AUC and the corrected
test, with the actual effect size stated. Two designs do not establish broad
hardware generality. Results must not be selected by solve rate or a favorable
target after reading AUC.

Incomplete matrices may show progress but must not enter confirmatory
inference. Unknown provider usage is explicitly flagged; reported cost is
then a lower bound, not a complete accounting. Each evaluation cell must have
its captured source/configuration manifest and archived compact trial ledger.

The endpoint currently measures RTL activity-profile synthesis. These
comparisons alone do not validate power prediction, structural workload
expressiveness, compositional targets or temporal targets. Those require
their own measurements and finalist gate-level validation.
