# AES held-out semantic agent

Complete panel: semantic-edits-v4 × five targets × ten held-out seeds
(200–209), 50 proposed slots per cell, batch size 4, epsilon 0.02.
Uses the transaction backend and frozen AES calibration.

All 50 cells and 2,500 proposal slots passed independent ledger audit.
Every original run manifest matches the frozen executable source hashes,
schema, model, prompt hash, sampling, pricing, calibration and useful-work
floor in `results/semantic_evaluation_freeze.json`. The target/seed grid is
complete. Invalid proposals and right-censored unsolved runs are retained.

Three batches have unknown provider usage. Estimated costs are therefore
incomplete, not a verified billing total. See per-cell summaries and trial
ledgers for usage and failures. Vertex calls ran serially on a shared host;
wall-clock values are not a controlled runtime comparison.

Pair with `results/aes_semantic_heldout_cpu/`. Confirmatory inference waits
for the complete DMA panels as required by `docs/HELD_OUT_PROTOCOL.md`.
These are activity-target experiments, not validation of power prediction
or structural workload expressiveness.
