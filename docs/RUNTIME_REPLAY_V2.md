# Runtime replay v2

Before updated-runtime smokes, replay AES and mesh's entire original 64-proposal
calibration corpus and all 18 admitted witnesses. No new random draw, target
change, normalization change or tolerance change is allowed. Each fixed case
counts, including duplicates. Run 18 independent cases concurrently per design.

Freeze the input programs, expected measurements, original bank and source
lineage before executing. Compare validity, stage, eight rates and the complete
profile exactly, including useful work, window and scope. Any mismatch prevents
promotion; report it rather than introducing an approximate compatibility rule.
This tests numerical compatibility of these 82 inputs, not all possible programs
or equivalence of the changed random policy. New studies use the new fingerprint;
historical results and banks remain unchanged. No model calls are involved.

`analysis/runtime_replay.py plan` freezes inputs; `scripts/probe_fixed_cases.py`
executes them through the shared backend. `analysis/runtime_replay.py audit`
checks completed replay records against the frozen expectations. Preserve the
archive and exact lineage before admitting a bank to updated-runtime smokes.
