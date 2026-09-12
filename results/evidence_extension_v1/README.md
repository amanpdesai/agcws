# Existing-evidence extension v1

Index, not a second findings narrative: see
[RESULTS.md](../../RESULTS.md#budget-cost-and-coverage-secondary-analysis).
No simulation, synthesis or provider calls were made for this bundle.

- [analysis.json](analysis.json): 36 cell prefixes at 16/32/64/128, arm costs,
  paired seed differences, scalar corpus coverage, provenance and missing-data limits.
- [workloads/](workloads/): 15 readable JSON examples. Each carries the workload
  or program, measured profile, source and selection rule. AES/DMA low/mid/high
  are nearest observed levels, not guaranteed tolerance solves. Ibex levels
  are observed mean-rate order statistics, not a calibrated scalar envelope.
- Four `*_temporal_random_*` files retain the predeclared random-policy AES/DMA
  finalists and their archived windowed GLS power. AES burst/ramp records retain
  the original capability-check shape names; a name does not certify target fit.
  No burst/ramp label is invented for Ibex or DMA. These are distinct backend
  grammars: use their recorded source flow, not one interchangeable runtime API.
- [control_readiness.json](control_readiness.json): historical/current offline
  phase-GA, compiler, reference-state and metric comparison. Synthetic mock losses
  are test fixtures, **not additional experimental results**.
- [PHASE_GA_ROBUSTNESS_V1.md](../../docs/PHASE_GA_ROBUSTNESS_V1.md): frozen scientific
  protocol; live identity/replay and final execution-manifest gates remain open.

## Reproduce without running hardware or models

Restore packed evidence to a new, explicit path first:

```bash
PYTHONPATH=src .venv/bin/python -m agcws.pipeline evidence-extract --study nonflat_temporal_v1 --destination /absolute/new/review
PYTHONPATH=src .venv/bin/python -m analysis.evidence_extension --archive /absolute/new/review/results/nonflat_temporal_v1 --out results/evidence_extension_v1 --verify
PYTHONPATH=src .venv/bin/python -m analysis.control_readiness --archive /absolute/new/review/results/nonflat_temporal_v1 --out /absolute/new/control-readiness.json
```

The secondary report/suite verification compares every generated JSON exactly.
The readiness probe restores verified historical source into a temporary tree
and compares it with current code in isolated Python processes. It does not
invoke compilers, simulators, containers or a model. Source hashes intentionally
change if the implementation changes; preserve this frozen report.

`inputs_sha256` binds original evidence (including restored paths) and
`analysis_source_sha256` binds the secondary implementation. `freeze.json` binds
the protocol, code and generated bundle. No old manifest was edited.

## Accounting limits

Cost is estimated from archived usage and historical rates, including thinking.
The denominator for cost per solve includes spending on unsolved cells and all
calls through the budget, even after a solve. Unknown-call reservations are
separate; this is not an invoice or early-stopping deployment cost. CPU cost is
unpriced, not zero. Prior studies and other cloud resources are not included in
this confirmation's liability. Actual credit balance, provider reconciliation
and organizer access remain externally unverified; no funding shortage is inferred.
