# AES all-target Flash/random/GA smoke

Complete: 54 cells, 324 slots, seed 8500, six slots per arm per target. Both
splits include eight nonflat targets and the control. All 36 Flash calls have
known usage: estimated cost $0.40203, unknown liability $0.

The strict measured-generated-feedback gate passes 12/18 targets. Remaining
targets lack a valid first generated batch for the second call. Exact work/idle
arithmetic violations dominate rejection. API success is not readiness. No
automatic retries or repaired workloads were introduced. `audit.json` reports
every target; `evidence/` retains raw responses, payloads, trials and caches.
This is plumbing evidence, not paper inference.
