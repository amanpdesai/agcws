# Balanced stronger-baseline development archive

Historical artifact notes. Current findings are consolidated in [RESULTS.md](../../RESULTS.md).
Commands referencing retired study/report modules require the [isolated historical source](../../archive/README.md), not the active checkout.

Complete: 36 cells, 576 charged proposals, 540 selected evaluations, 36 filtered
unknown-validity proposals, zero model calls. Twelve construction attempts and
all three measured witness targets are retained. See
[results and claim limits](../../RESULTS.md).

- `manifest.json`: producer commit, source/runtime identity, constructors, seeds,
  policy set, proposal budget and selection rule. Committed before construction.
- `witnesses.json`, `targets.json`: all construction outcomes and selected target
  profiles. Witness evidence was checked and targets committed before search.
- `cells.json`: every cell, candidate, parent, pre-measurement decision and result.
- `summary.json`: AUC first, all per-cell curves, solve/censoring, accounting,
  equal-valid secondary results and descriptive matched seed differences.
- `evaluations/`: 233 unique compressed CPU evidence bundles, including failed
  useful-work cases. No VCD/FST waveform is committed.
- `difficulty_diagnostic.json`: explicitly post-hoc constant-vector diagnostic,
  with hashes of the target and summary inputs. It did not select targets.

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m experiments.baseline_panel_v1.study audit
.venv/bin/python -m analysis.baseline_panel_v1_diagnostics
```

Initialize the pinned GeST submodule and match the manifest's numerical/runtime
dependencies. Auditing checks compact records, not independent simulation.
The original scratch directory is `out/baseline-panel-v1`; committed manifests
and immutable checkpoints permit deterministic resume. Targets and existing
results cannot be silently replaced. Shared cache warmth makes per-arm wall-clock
comparisons inappropriate; selected-evaluator counts are reported separately.

The actual matched contrast is ridge screening versus the four-proposal GeST
pool. The two-proposal GeST arm is a feedback-frequency control. This is a
two-seed development panel, not evidence of published SAGA reproduction, a
held-out superiority claim, or an agent-vs-baseline comparison.
