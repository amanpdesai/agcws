# V3 temporal development — implementation gate only

The integral-number CPU equivalence gate passes: identical emitted assembly,
architectural state, markers and activity bins to the v2 partial-iteration case.
The retirement feedback uses exactly the same observation interval.

This directory does **not** contain a completed ablation. No comparative model
calls have been made. The 72-cell design is described in
[the draft protocol](../../docs/IBEX_TEMPORAL_V3_DEVELOPMENT.md); source/controller
freeze and experiment execution are still pending.
