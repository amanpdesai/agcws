# Reproducible result archives

This directory contains compact review artifacts from completed experiments.
Large waveforms, logs, and per-trial scratch files remain under ignored `out/`.

## AES scalar matrix

`aes_scalar_matrix_50/` contains 300 summaries: six policies, five targets, ten
seeds, 50 proposal slots per run, and epsilon 0.02. Unsolved runs are retained
with `evaluations_to_target=50` and `right_censored=true`. The primary endpoint
is `auc_best_so_far`; solve rate is secondary.
