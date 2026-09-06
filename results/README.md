# Reproducible result archives

This directory contains compact review artifacts from completed experiments.
Large waveforms, logs, and per-trial scratch files remain under ignored `out/`.

## Eight-window gate validation

`windowed_power_v1/` contains 16 predeclared finalists and four matched achieved
references: eight native windows plus a full-span report each (180 reports).
It includes exact durations, raw Tcl/reports, input hashes, reference replay
checks and executed measurement-source snapshots. Working sources received
style and synthetic-fixture filename cleanup afterward; snapshots preserve the
code actually measured.
`window_semantics_v1/` holds tiny synthetic traces as `.vcd.txt` test inputs,
not design waveforms, with independent state/density/duty checks at two timescales.

Review without simulators, cloud calls or the large local VCDs:

```bash
.venv/bin/python -m analysis.audit_windowed_archive
.venv/bin/python -m analysis.report_windowed_power
```

The renderer regenerates `docs/WINDOWED_POWER_RESULTS.md` and the four-panel
figure used in `paper/report.pdf`. The compact audit checks report arithmetic,
hashes, original selection, reference normalization and annotation; independently
regenerating the measurements requires the raw/replayed waveforms and toolchain.
See `validation/README.md` and `docs/WINDOWED_POWER_PROTOCOL.md`.

`structural_valid_evaluation_diagnostic_v1.json` is a post-hoc conditional
equal-valid-evaluation analysis, not a replacement for proposal-counted inference.
Regenerate to a new output path with `python -m analysis.structural_valid_diagnostic --out <new.json>`.

## Frozen structural temporal study

`structural_temporal_heldout_v1/` contains the 160 independently audited cells
(5120 charged proposal slots), their compact ledgers/manifests and seed-clustered
inference in `heldout.json`. The development comparison is separately archived
in `structural_population_development_v1/`; selection and configuration are
fixed in `structural_temporal_freeze_v1.json`.

`structural_temporal_finalists_v1.json` selects 16 seed-400 cases without gate
scores. `structural_temporal_finalist_validation_v1/` contains all 16 matched
GLS comparisons, raw power reports, functional logs, provenance and each
waveform's own timescale/span. No waveforms are committed.

The report is `docs/STRUCTURAL_RESULTS.md`. Recreate its text without cloud
calls or simulator execution (choose a new output path):

```bash
.venv/bin/python -m analysis.report_structural_results \
  --heldout results/structural_temporal_heldout_v1/heldout.json \
  --validation results/structural_temporal_finalist_validation_v1/validation.json \
  --out /tmp/agcws-structural-report-review.md
```

Re-audit the compact ledgers without rerunning search:

```bash
.venv/bin/python -m analysis.audit_structural_heldout \
  --source results/structural_temporal_heldout_v1 \
  --freeze results/structural_temporal_freeze_v1.json \
  --archive /tmp/agcws-structural-review-audit
```

The audit verifies manifests, proposals, costs, target losses and full-panel
inference against the frozen source/corpus configuration. Full independent
waveform-span reconciliation requires the raw local run and replay directories;
the compact archive preserves the measured spans and hashes, not those large
traces. See `validation/README.md` to reproduce the gate replays.

## Current held-out semantic study

`semantic_heldout_comparison.json` combines 550 independently audited cells:
`aes_semantic_heldout_cpu/`, `aes_semantic_heldout_agent/`,
`dma_semantic_heldout_cpu/`, and `dma_semantic_heldout_agent/`.
Original manifests, compact ledgers and summaries are tracked. Selection and
freeze are recorded in `semantic_controller_selection.json` and
`semantic_evaluation_freeze.json`. Read `docs/SEMANTIC_RESULTS.md` for the
complete primary/secondary findings and claim limits.

## Historical AES scalar matrix

`aes_scalar_matrix_50/` contains 300 summaries: six policies, five targets, ten
seeds, 50 proposal slots per run, and epsilon 0.02. Unsolved runs are retained
with `evaluations_to_target=50` and `right_censored=true`. The primary endpoint
is `auc_best_so_far`; solve rate is secondary.
This older harness/calibration is not pooled with the current transaction
and pipelined held-out study.
