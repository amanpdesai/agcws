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

The active foreground pipeline writes checkpoints and logs under
`out/phase-ga-robustness-v1`. This directory does not yet contain a completed
panel or new comparison result. Use the maintained `pipeline status` command;
do not infer completion from gate success or an execution manifest.

The tested compact-export utility is `maintenance.archive_study`: it wraps the
existing pipeline exporter and evidence verifier, preserves raw scratch, and
can restore exact compact bytes for re-analysis. It is not another study runner.
