# V4 short-allocation CPU gate

Historical artifact notes. Current findings are consolidated in [RESULTS.md](../../RESULTS.md).
Commands referencing retired study/report modules require the [isolated historical source](../../archive/README.md), not the active checkout.

The retained v2 `tiny` development program exercises allocations shorter than
their loop body. Original and phase-labeled compilations have byte-identical
loadable programs, architectural state, observation markers, activity-bin counts,
retirement classes and completion time. `gate.json` hashes the compact evidence.
This complements the partial-iteration gate in `ibex_temporal_v4_gate/`; neither
is a temporal policy comparison. Large waveforms and retirement traces remain
local scratch. The pinned simulator was reused without rebuilding or modification.
