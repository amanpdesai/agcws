# DMA held-out CPU baselines

Historical artifact notes. Current findings are consolidated in [RESULTS.md](../../RESULTS.md).
Commands referencing retired study/report modules require the [isolated historical source](../../archive/README.md), not the active checkout.

Complete panel: four policies × five targets × ten held-out seeds (200–209),
50 proposed slots per cell, batch size 4, epsilon 0.02. Policies are random,
mutation, evolutionary and scalar-edit-evolution. Uses the pipelined backend
and frozen DMA calibration. No DMA coverage-guided arm is claimed.

All 200 cells and 10,000 proposal slots passed independent ledger audit.
Every original run manifest matches the frozen executable source hashes,
schema, calibration, useful-work floor and environment configuration in
`results/semantic_evaluation_freeze.json`. The policy/target/seed grid is
complete. Invalid proposals and unsolved runs remain in the archive;
unsolved evaluations-to-target are right-censored at 50.

CPU concurrency changed from four to eight workers at a completed-cell
boundary. `scheduling_handoff.json` records the handoff, and completed cells
were reused without rerunning their trials. The resumed process exited zero.
This shared-host scheduling is not a controlled policy-runtime comparison.

Final inference requires the complete matching DMA agent panel and both AES
panels under `docs/HELD_OUT_PROTOCOL.md`. These are activity-target results,
not evidence of gate-power prediction or structural workload expressiveness.
