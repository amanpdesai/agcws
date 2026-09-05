# DMA held-out semantic agent

Complete panel: semantic-edits-v4 × five targets × ten held-out seeds
(200–209), 50 proposed slots per cell, batch size 4, epsilon 0.02.
Uses the pipelined backend and frozen DMA calibration.

All 50 cells and 2,500 proposal slots passed independent ledger audit.
Every original source/configuration manifest matches the recorded evaluation
freeze. The policy/target/seed grid is complete. Invalid proposals and
right-censored unsolved runs remain in the archive. The serial process
completed with exit status zero; no evaluation cells were rerun for selection.

Five batches have unknown provider usage; estimated cost is incomplete.
Per-cell summaries and compact ledgers retain the failure and cost accounting.
Shared-host wall-clock values are not a controlled runtime comparison.

Pair with `results/dma_semantic_heldout_cpu/` and both AES panels. The complete
predeclared analysis is `results/semantic_heldout_comparison.json`, interpreted
in `docs/SEMANTIC_RESULTS.md`. These are scalar activity-target experiments,
not gate-power validation or structural workload expressiveness results.
