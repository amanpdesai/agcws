# DMA baseline development — complete panel

All 60 cells are complete: four policies × five targets × three development
seeds, 50 proposal slots per run. All 3,000 proposal slots passed independent
ledger audits. `aggregate.json` is the complete descriptive summary.

| Policy | Mean AUC ↓ | Solved / 15 | Valid proposals |
|---|---:|---:|---:|
| random | 2.0764 | 9 | 100% |
| evolutionary | 4.3431 | 9 | 99.5% |
| scalar-edit-evolution | 5.2186 | 3 | 21.9% |
| mutation | 5.6657 | 6 | 99.3% |

The scalar-edit control matches the semantic edit representation, but its
poor protocol compliance makes it a weak stand-alone optimization baseline.
An agent advantage over it could reflect legality rather than search quality;
the random and design-aware mutation/evolutionary arms remain essential.

After eleven cells completed serially, the remaining cells resumed under
four managed CPU workers. Completed cells were reused without simulation.
`execution.json` records this scheduling-only change. Seeds, targets,
calibration and budgets remain unchanged; wall-clock figures must not be
pooled as a controlled serial-performance comparison.

The agent ran separately and serially; its complete comparison is in
`results/dma_pipelined_development_agent/comparison.json`.
These are activity-search development
results, not held-out or gate-power results.
