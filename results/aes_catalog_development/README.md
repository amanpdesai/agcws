# AES catalog-controller development

Complete 15-cell panel: five scalar targets, seeds 100–102, 50 proposed slots
per run, batch size 4, epsilon 0.02. Uses the transaction backend and its
frozen calibration; all 750 slots independently audited.

Primary mean AUC (lower is better): V5 1.2604, V4 1.6073, matched scalar-edit
evolution 1.7473, random 2.1849, instrumented line-coverage search 2.8559.
V5 solves 14/15 and emits 93.1% valid proposals. These are descriptive
development results, not held-out superiority or equivalence evidence.

Recorded estimated cost is $0.6743 at the configured rates, with two batches
of unknown provider usage: this is incomplete cost accounting, not a full bill.
`comparison.json` records all seven policies and their source panels.
Each cell includes its original run manifest, compact trial ledger and summary.

No controller has been selected from this AES-only result. Selection also
requires the complete DMA V5 panel under `docs/HELD_OUT_PROTOCOL.md`.
