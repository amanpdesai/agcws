# Reproducible result archives

This directory contains compact review artifacts from completed experiments.
Large waveforms, logs, and per-trial scratch files remain under ignored `out/`.

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
