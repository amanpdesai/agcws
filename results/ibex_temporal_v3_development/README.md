# V3 temporal development — complete

Historical artifact notes. Current findings are consolidated in [RESULTS.md](../../RESULTS.md).
Commands referencing retired study/report modules require the [isolated historical source](../../archive/README.md), not the active checkout.

The integral-number CPU equivalence gate passes: identical emitted assembly,
architectural state, markers and activity bins to the v2 partial-iteration case.
The retirement feedback uses exactly the same observation interval.

This directory contains all 72 completed cells and 1,152 requested slots. The study
was frozen at `dca1344` before model calls and ran in supervised workers.
See [the protocol](../../archive/README.md) and `manifest.json`.
No completed v1/v2 result has been modified. The full compact-data audit passes.
See [the report](../../RESULTS.md), `aggregate.json`, and
`finalists.svg` (all seeds and policies, not selected examples).

The compact archive retains every run, frozen source,
context receipt and evaluation record. Copied RTL retains its original license
headers; its license is included as `RTL_LICENSE` beside the context bundle.
Large simulator waveforms and retirement traces remain local scratch.

Run `python -m analysis.ibex_temporal_v3 --archive
results/ibex_temporal_v3_development --verify` from the repository root with its
dependencies installed. This checks compact evidence and arithmetic, not a fresh
simulation. No held-out superiority, intrinsic expressiveness, or power claim is
made. Nested-program diagnostics are post-hoc checks only; failures retain their
original budget charges and are not rescored.
