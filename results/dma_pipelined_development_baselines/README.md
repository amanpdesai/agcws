# DMA baseline development — incremental archive

This panel is still running. The manifest declares four policies × five
targets × three development seeds, 50 proposal slots per run. The completed
cells listed in `summaries.json` have passed independent ledger audits.
The final aggregate command refuses incomplete panels.

After eleven cells completed serially, the remaining cells resumed under
four managed CPU workers. Completed cells were reused without simulation.
`execution.json` records this scheduling-only change. Seeds, targets,
calibration and budgets remain unchanged; wall-clock figures must not be
pooled as a controlled serial-performance comparison.

The agent runs separately and serially. These are activity-search development
results, not held-out or gate-power results.
