# Test map

- `unit/`: schemas, compilation, policies, parsers, metrics and failure cases.
- `integration/`: shared runner/recovery, CLI, packaged assets, CHIA and DMA tool checks.
- `regression/`: frozen contracts, archive integrity, accounting and published-evidence replay.
- `fixtures/`: checked-in inputs and golden schema fingerprints.

Run all checks with `make test`; a directory can be selected with
`.venv/bin/pytest -q tests/regression`. Tests do not purchase model calls.
Tool-backed checks require their documented local dependencies; a passing unit
subset is not a substitute for the complete release gate.

Full published-panel audit and Docker smoke are separate explicit checks. See
[architecture and workflow](../docs/ARCHITECTURE.md) for commands and dependencies.
