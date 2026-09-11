# Proposal interface v2 — development evidence

Historical artifact notes. Current findings are consolidated in [RESULTS.md](../../RESULTS.md).
Commands referencing retired study/report modules require the [isolated historical source](../../archive/README.md), not the active checkout.

Status: **complete**. The 36-cell, 576-slot comparison was frozen at `1eb5106`
before its first call. Model-generated validity is 157/168 (93.45%), passing the
predeclared gate. Agent mean AUC is 4.554168 versus random 4.831839: descriptive
development evidence, not held-out superiority. Both solve 3/12 cells.

The gate covers partial iterations, allocations shorter than a body, conditional
control and memory effects. The embedded v1 witness reproduces its architectural
state, markers and all eight activity bins exactly. Gate inputs, emitted assembly,
architectural output and profiles are retained here; large FST traces remain in
the local artifact directory.

See [the protocol](../../archive/README.md) and the frozen
`manifest.json` for the 36-cell model/baseline comparison.
No completed v1 result or source has been changed.

[Full findings and limits](../../RESULTS.md).
`aggregate.json` records every policy; `readiness.json` excludes shared
initialization. `finalists.svg` shows all seeds rather than selected examples.

Verify the compact archive without simulation or cloud access:

```sh
.venv/bin/python -m analysis.ibex_proposal_v2 --archive results/ibex_proposal_v2_development --verify
```

The audit also checks that all 192 random slots reproduce v1 exactly. Large FST
waveforms are local scratch, not part of this compact evidence archive.
