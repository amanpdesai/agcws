# Solution audit evidence

Findings live only in [RESULTS.md](../../RESULTS.md). This is an offline, post-hoc
audit with selection frozen before detailed inspection, not a held-out study.

- `selection.json`: immutable role selection and source trial hashes, committed
  at `7e43ae8d4`; protocol committed at `fa43ac439`.
- `inspection.json`: selected programs, observable explanations, execution
  diagnostics, payload hashes and scoped consistency checks.
- `work.json`: state-change instrumentation checked against actual printed
  architectural output; not a revised useful-work definition.
- `case_notes.json`: human inspection keyed to exact target/seed/policy/slots.
- `traces/*.json`: independently counted microbins from retained FSTs;
  `summary.json` pairs candidates with measured witness profiles.
- `inventory.json`: evidence, code and original-source checksums.
- `verification.json`: completed checks and their scope.

From the repository root, with the Python environment installed:

```bash
PYTHONPATH=src .venv/bin/python -m analysis.solution_inspect --out /tmp/inspection-review.json
PYTHONPATH=src .venv/bin/python -m analysis.solution_trace_audit --out /tmp/trace-review
.venv/bin/pytest -q tests/test_solution_audit.py
PYTHONPATH=src .venv/bin/python -m analysis.solution_audit_inventory --verify
```

Output paths must not already exist. Trace reconstruction additionally requires
`fst2vcd` and retained waveforms under `out/nonflat-temporal-v1/cache/`; compact
results alone cannot recreate deleted waveforms. No command above simulates RTL
or calls a model. `analysis.solution_work_audit` writes `work.json` exclusively;
run in a separate checkout without that output to reproduce it.

Archived pre-consolidation source is `archive/legacy-source.tar.gz`, indexed by
`archive/manifest.json`. Reference/payload reconstruction uses migrated code and
is not an independent oracle. The streaming waveform counter and architectural
state-change instrumentation are separate offline implementations with synthetic
tests. Interpretation is limited to their inspected scope.
