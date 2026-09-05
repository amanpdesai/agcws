# Semantic search held-out protocol

Declared 2026-09-05, before running seeds 200–209.

Development uses seeds 100–199 only. Finish all five targets on AES and DMA
before selecting and recording a controller version. Any later controller,
prompt, schema or evaluator change requires a new version and a new evaluation;
do not combine versions as one method. Selection is documented, not automatic
stopping when a promising cell finishes.

Controller selection is between semantic-edits-v4 and semantic-catalog-v5,
using all five targets and development seeds 100–102 on both designs.
Choose the lower arithmetic mean AUC across the 30 design/target/seed cells;
the balanced panel weights both designs equally. Keep invalid proposals and
unsolved runs. Require all cells and ledger audits before selection; do not
choose a different controller per design. An exact numerical tie selects v4.
Record both candidates' results and the selected prompt/model/source hashes
before running any held-out seed. This rule was recorded before v5 development
started, with v4 DMA still incomplete. It selects a candidate, not a favorable
research conclusion: held-out losses and null results must still be reported.

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

CPU and agent panels may run separately. Pass all panels for each design to
`scripts/compare_semantic_evaluation.py --aes <panels...> --dma <panels...>
--agent <frozen-policy> --out <comparison.json>`. The loader checks matching
conditions (including calibration, model and prompt), disjoint policies,
complete cells and each ledger before the full-matrix inference checks.
Original source manifests remain attached to the output; separate scheduling
does not make wall-clock results a controlled parallel-runtime comparison.

For the final report, use the stricter wrapper below. It additionally compares
every cell's source/configuration manifest against the recorded freeze,
archives input-file hashes, and emits descriptive AUC, solve/censoring,
validity and cost-accounting totals alongside the same predeclared inference.
It refuses incomplete panels and will not overwrite an existing report.

```bash
.venv/bin/python -m analysis.report_semantic_evaluation \
  --aes results/aes_semantic_heldout_cpu results/aes_semantic_heldout_agent \
  --dma results/dma_semantic_heldout_cpu results/dma_semantic_heldout_agent \
  --out results/semantic_heldout_comparison.json
```

The endpoint currently measures RTL activity-profile synthesis. These
comparisons alone do not validate power prediction, structural workload
expressiveness, compositional targets or temporal targets. Those require
their own measurements and finalist gate-level validation.
