# GeST phase-bridge CPU qualification

Completed 2026-09-10. This is an integration check, not a comparative study.
The [frozen protocol](../../docs/GEST_BRIDGE_V1.md) declares eight proposals,
one existing achieved target, seed 840, two proposals per batch, and no model
calls. `manifest.json` pins producer hashes, upstream operator hashes, target
source and measurement identity; its source commit precedes execution.

- Eight slots completed: two bootstrap and six upstream-operated offspring.
- Seven valid; one useful-work rejection with no loss. No replacement retry.
- Two cache hits still consumed proposal slots; six cache-miss evaluations.
- Best normalized temporal activity error: 0.1068908277240853.
- No Vertex calls or cloud inference spend.

There is no random/agent control in this smoke. It cannot establish GeST
efficacy, competitiveness or reproduction of the published algorithm. The
phase genotype and external ask/tell scheduler are explicit adaptations;
SAGA has not been connected to temporal loss.

`trials.json` contains every proposal, parent slot, measured outcome and cache
flag. `evaluations/` stores gzip-compressed CPU logs, generated assembly,
functional reference records and activity profiles, not waveforms. No pickle
from an external artifact is loaded. Heavy scratch stays in `out/gest-bridge-v1`.

```bash
.venv/bin/python -m experiments.gest_bridge_v1.qualification audit
```

The audit reconstructs proposals and parent visibility from the pinned upstream
operators, checks scores against the actual target, validates CPU state and
assembly against the reference interpreter/compiler, and verifies rate/window
arithmetic and provenance. It does not independently rerun simulation or prove
waveform integrity from logs alone. Initialize submodules before auditing.

The runner can resume deterministically using its checkpoint directory; completed
slots are read, not simulated again. The frozen manifest must be committed and
runtime/source identities must match. Invalid results are never assigned fitness.
