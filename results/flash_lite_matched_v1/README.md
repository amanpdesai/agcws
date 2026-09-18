# Matched Flash-Lite matrix — completed 2026-09-18

450 cells, five designs × nine profiles × ten seeds. All final runners exited
successfully. The single authoritative comparative table and interpretation are
in [RESULTS.md](../../RESULTS.md#matched-five-design-flash-lite-results--2026-09-18).

## Evidence index

- [summary.json](summary.json): all Flash curves/cells, matched CPU aggregates,
  nonflat paired inference, control results, validity, cache and accounting audit.
- [secondary.json](secondary.json): nonflat 16/32/64/128 AUC/solve slices,
  equal-observed-valid-evaluation diagnostics and cost-per-solve estimates/bounds.
- [archive-verification.json](archive-verification.json): exact-byte restoration receipts.
- [verification.json](verification.json): publication audit and 810-test validation receipt.
- [timing.json](timing.json): completion-time snapshot and separate latency/
  evaluation-time totals; elapsed time includes the manual budget pause.
- [Frozen protocol](../../docs/FLASH_MATCHED_V1.md) and
  [launch manifests](../flash_lite_matched_v1_plan/README.md).
- [Matched CPU summary](../baselines_model_v1/README.md): not rerun or retuned.
- [Accounting-only resume](../flash_budget_resume_v1/README.md): Mesh and RedMulE
  stopped at conservative caps; all original records and failure receipts retained.

Packed, bounded evidence shards per design:
[AES](../aes/flash-lite-matched-v1/), [DMA](../dma/flash-lite-matched-v1/),
[Ibex](../ibex/flash-lite-matched-v1/), [Mesh](../mesh/flash-lite-matched-v1/),
[RedMulE](../redmule/flash-lite-matched-v1/). No VCDs or compiled simulators in git.

## Reproduction without simulation or model calls

Restore each Flash archive and the corresponding CPU archive beneath separate
roots, using design names aes/dma/ibex/mesh/redmule. Example:

```sh
.venv/bin/python maintenance/archive_study.py restore \
  --source results/aes/flash-lite-matched-v1 --destination /tmp/agcws-flash-review/aes
.venv/bin/python maintenance/archive_study.py restore \
  --source results/aes/baselines-model-v1 --destination /tmp/agcws-cpu-review/aes
# Repeat for the other four designs, then:
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m analysis.publish_flash_matrix \
  --root /tmp/agcws-flash-review --baselines /tmp/agcws-cpu-review \
  --output /tmp/agcws-flash-summary.json
.venv/bin/python -m analysis.flash_matrix_secondary \
  --flash /tmp/agcws-flash-summary.json \
  --baseline results/baselines_model_v1/summary.json \
  --output /tmp/agcws-flash-secondary.json
```

The audit uses a read-only saved-response provider. It reconstructs every
same-cell prior-history payload and re-decodes every response without asking
the model again. Missing required records cause failure, not substitution.
It checks the same initial programs, target/seed/scale/gate/budget/schema/runtime
contracts, scored cache identities and rates, metric arithmetic, early stops,
right-censoring, saved summaries, and accounting adjustment hashes. Baseline
trajectories reproduce the already-published CPU summary, whose hash is pinned.
It does not reproduce provider sampling or independently resimulate waveforms.

The primary comparison averages eight nonflat targets within each seed, uses
ten seed units/design and fifteen Holm-adjusted comparisons; controls are not
in the primary mean. Equal-valid comparisons are secondary observed-prefix
diagnostics, not a change to proposal-counted budgets. Zero solves yield null
cost-per-solve, not zero cost. Pricing estimates exclude any unverified discounts
or credits; unknown-token reservations are never labeled billed spend.

The model was explicitly `gemini-3.5-flash-lite` with MEDIUM thinking. Do not
label this a 2.5 Flash study or compare it directly to older Pro panels on
different targets. The target bank was already observed during engineering.
Strict ≤0.05 feasibility remains unproven for every request; failures are not
proof of infeasibility. No claim of general semantic understanding or general
agent superiority follows from the cross-design pattern.
