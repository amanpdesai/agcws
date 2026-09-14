# DMA all-target Flash/random/GA smoke

Complete: 54 cells, 324 slots, seed 8500, six slots per arm per target. Both
splits include eight nonflat targets and the control. All 36 Flash calls have
known usage: estimated cost $0.3987989, unknown liability $0.

The strict measured-generated-feedback gate passes 13/18 targets. Exact-budget
protocol violations leave some targets without a valid first generated batch
for the second call. No retries, silent repairs or tolerance changes were used.
`audit.json` retains per-target outcomes; `evidence/` retains all payloads,
responses, trials and cached measurements. Full-bank readiness is not claimed.
