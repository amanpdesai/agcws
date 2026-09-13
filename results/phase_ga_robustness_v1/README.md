# Phase-GA robustness extension

Current findings and execution status are in [RESULTS.md](../../RESULTS.md).
This is post-hoc robustness on the observed confirmation targets, not fresh
held-out confirmation. No model calls are included.

- [execution_manifest.json](execution_manifest.json): exact maintained-runner
  configuration, sources, immutable image ID and binary identity.
- [execution_freeze.json](execution_freeze.json): pre-execution hashes, panel
  size, authorization scope and resource-accounting limits.
- [gate/](gate/): frozen seven-program selection, original/runtime identities,
  individual exact comparisons and gate completion. Raw replay traces/logs are
  retained locally in `out/phase-ga-robustness-v1-gate`.
- [protocol](../../docs/PHASE_GA_ROBUSTNESS_V1.md): untuned algorithm, all-slot
  accounting, pairing, two-contrast Holm correction and failure behavior.
- [analysis.json](analysis.json): audited cell metrics, prefixes, paired inference,
  validity, equal-valid secondary results and source evidence checksums.
- [verification.json](verification.json): completion, frozen identities, compact
  restoration/re-analysis and test checks performed before publication.
- [host-resources.log](host-resources.log): successful exit and elapsed time;
  CPU figures exclude container processes.
- `evidence.pack.json.gz` and `evidence-000.tar.gz`: checksummed compact export,
  restoring 32,992 exact raw files. Waveforms and instruction traces are excluded;
  JSON records, emitted assembly and functional logs are retained.

All 18 cells / 2,304 slots completed without infrastructure failures. The raw
scratch directory is `out/phase-ga-robustness-v1`; publishing the compact archive
does not delete it. Findings are in the single authoritative RESULTS.md, not
duplicated here. The audit checks stored state/counts and accounting, not a fresh
simulation of every waveform.

## Reproduce without simulation or model calls

Run from the repository root with dependencies installed. Each destination must
be new. Historical evidence extraction makes a review workspace linked to this
checkout; treat its linked files as read-only.

```bash
PYTHONPATH=src .venv/bin/python -m agcws.pipeline evidence-extract \
  --study nonflat_temporal_v1 --destination "$PWD/out/ga-history-review"
PYTHONPATH=src .venv/bin/python -m maintenance.archive_study restore \
  --source results/phase_ga_robustness_v1 --destination out/ga-compact-review
PYTHONPATH=src .venv/bin/python -m analysis.phase_ga_robustness \
  --root out/ga-compact-review \
  --historical out/ga-history-review/results/nonflat_temporal_v1 \
  --gate results/phase_ga_robustness_v1/gate \
  --out out/ga-reanalysis.json
cmp out/ga-reanalysis.json results/phase_ga_robustness_v1/analysis.json
```

The compact-export utility wraps the existing pipeline exporter and verifier;
it is not another study runner. Source identities in the execution manifest
describe the code that ran, while the archive's producer commit identifies its
packaging implementation. The frozen analysis was not changed after execution.
