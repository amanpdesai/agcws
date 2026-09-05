# AES held-out CPU baselines

Complete panel: five policies × five targets × ten held-out seeds (200–209),
50 proposed slots per cell, batch size 4, epsilon 0.02. Policies are random,
mutation, evolutionary, scalar-edit-evolution and instrumented line-coverage
search. Uses the transaction backend and frozen AES calibration.

All 250 cells and 12,500 proposal slots passed independent ledger audit.
Every captured executable source digest matches
`results/semantic_evaluation_freeze.json`. Each cell has its original run
manifest, compact trial ledger and summary. Invalid and unsolved proposals
are retained; unsolved evaluations-to-target are right-censored at 50.

Four managed CPU workers ran this panel on a shared host. Wall-clock values
are not a controlled parallel-runtime comparison. No agent superiority or
equivalence inference follows from this baseline-only panel; the complete
AES and DMA policy matrices are required by `docs/HELD_OUT_PROTOCOL.md`.
