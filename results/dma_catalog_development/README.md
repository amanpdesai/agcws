# DMA catalog-controller development

Complete 15-cell panel, all 750 proposed slots independently audited. Five
scalar targets, seeds 100–102, 50 slots, batch size 4, epsilon 0.02, pipelined
DMA backend and frozen calibration match the other development policies.

Primary mean AUC (lower is better): random 2.0764, V4 2.5116, evolutionary
4.3431, V5 5.0036, matched scalar edits 5.2186, mutation 5.6657. V5 solves
4/15 with 67.5% valid proposals. The catalog interface improved AES but
regressed on DMA; it does not establish cross-design improvement.

Invalid proposals include repeated AXI boundary and useful-work-floor failures.
All remain charged, and unsolved runs are censored at 50. Recorded estimated
cost is $1.1229 at configured rates, with five unknown-usage batches, so cost
accounting is incomplete. Cell ledgers retain failure and usage diagnostics.

`comparison.json` contains all six policies and their source panels. Each
cell includes its original run manifest, compact ledger and summary.
These are development results, not held-out inference.
