# Five-design, three-arm CPU baseline matrix

Completed 2026-09-17. This is post-hoc baseline robustness on an already-observed
bank, **not** a fresh held-out confirmation and not a comparison with an LLM.
The authoritative interpretation is in [RESULTS.md](../../RESULTS.md).

Five designs × nine confirmation profiles (eight nonflat plus flat control) ×
ten seeds (9100–9109) × three policies = **1,350 completed cells**. Each cell
has a 128-proposal maximum, shared two-proposal initialization, batch size two,
and stops at the first successful batch. Invalid proposals consume budget.
Success requires every bin's absolute error divided by the frozen calibration
width to be ≤0.05. RMSE best-so-far AUC is the primary reported score; lower is
better. Unsolved evaluations-to-target are right-censored at 128, never omitted.
After early stopping, terminal best RMSE is carried to 128 for the AUC.

The comparative table is maintained once, in
[RESULTS.md](../../RESULTS.md#completed-five-design-baseline-matrix--2026-09-17).

Each denominator is 90 cells. On AES, 33/40 model-guided solves are nonflat
(33/80); seven are controls. Its single DMA solve is a control. Random's AES
solve and GA's AES/DMA/Ibex solves are nonflat. No method solves Mesh or RedMulE.
Do not infer infeasibility from exhausted search budgets. Qualification used a
different acceptance rule; not every requested profile has a ≤0.05 max-bin witness.

`phase-model` is a fixed ridge-guided timing policy, not an LLM and not an exact
reproduction of PaTGen/SAGA/GeST. It optimizes worst-bin residuals, whereas the
unchanged GA selects by RMSE. Report this objective difference alongside the
new proposal representation; do not attribute the entire effect to its regressor.

## Evidence and reproduction

[summary.json](summary.json) retains every cell's full curve, AUC, solve status,
censoring, invalid-stage counts, charged/valid proposals, internal surrogate
candidate count, per-target and nonflat aggregates, and exploratory inference.
Inference averages targets within each seed before paired testing (ten seed
units/design), uses exact two-sided sign flips, 10,000 paired seed bootstraps,
and Holm adjustment across all fifteen design/policy contrasts. These are
post-hoc analyses, not newly preregistered confirmatory tests; target-family
generalization is not tested by seed resampling.

Packed compact evidence is split per design into bounded shards:

- [AES](../aes/baselines-model-v1/)
- [DMA](../dma/baselines-model-v1/)
- [Ibex](../ibex/baselines-model-v1/)
- [Mesh](../mesh/baselines-model-v1/)
- [RedMulE](../redmule/baselines-model-v1/)

[Verification](verification.json) records 777 passing tests and audit scope;
[archive receipts](archive-verification.json) record exact-byte restoration
counts per design.

Each export is stream-restored and byte-compared to its source before publication.
The explicit shard limit is 64 MiB to accommodate the large raw inventory
members; no compact evidence is omitted to fit that bound. The first 32 MiB
packing attempt exceeded the index/member limit and was superseded before
publication. The streaming packer avoids a loose temporary copy of every record.
Raw waveforms and compiled simulators remain local, outside the compact export.
Source/runtime identities and original plans remain at
`results/DESIGN/baselines-model-v1-plan/`. Runtime was frozen at `a025d4f9f`;
launch checkout was `d49d59393`, with no runtime-source changes during execution.

To restore one design and recompute its audit without simulation or APIs:

```sh
.venv/bin/python maintenance/archive_study.py restore \
  --source results/aes/baselines-model-v1 --destination /tmp/agcws-aes-review
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m analysis.publish_baseline_matrix \
  --design aes --root /tmp/agcws-aes-review --output /tmp/agcws-aes-audit.json
```

Restore all five beneath one directory using their short design names, then
omit `--design` to regenerate `summary.json`. The audit checks every score,
residual, parent visibility, cache identity/rates, early-stop prefix, summary and
panel total. It regenerates seed-only initializations and random/GA proposals.
For model-guided decisions it checks prior training-slot visibility, selected
program identity and no reported extra simulations; it does **not** independently
re-fit every ridge model or re-simulate waveforms.

## Cost and runtime

The matrix consumed **170,152 charged proposals** (maximum 172,800).
There were no provider requests and $0 model liability; this does not mean
CPU infrastructure or electricity was free. All five runners exited 0.
Up to eighteen cells/design ran concurrently (90 total). Approximate wall times
from the common launch timestamp to each completion file were AES 4.63 h,
DMA 5.45 h, Ibex 21.48 h, Mesh 4.88 h and RedMulE 12.05 h. These concurrent wall
times are not CPU-hours and exclude the subsequent publication audit.
Summed distinct-measurement subprocess elapsed time is reported separately in
the JSON; it excludes optimizer/archival overhead and can exceed wall time.

No paid runs were started as part of publication. Future agent comparisons must
match these exact tasks, measurement implementation, budget, gate and seeds, or
be versioned separately; historical Pro results are not interchangeable.
