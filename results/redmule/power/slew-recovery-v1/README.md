# RedMulE power validation

These 22 measurements retain the original selected workloads and native power
estimates. A signal-level audit explains the whole-trace/window discrepancy
through OpenSTA's slew-based activity cap. Functional completion, exact transition
counts, window alignment, annotation, and unchanged power reports are checked.

`index.json` binds the measurements and compact execution/proof evidence.
Original failed attempts remain in `../measurements.jsonl.gz`.

Verify the portable evidence:

```bash
PYTHONPATH=src .venv/bin/python -m agcws.reporting.redmule_recovery
```

To rerun the audit with the retained local waveforms and pinned OpenSTA:

```bash
PYTHONPATH=src .venv/bin/python -m agcws.reporting.redmule_recovery --audit out/redmule-audit-new --workers 8
```

Portable verification checks the recorded execution, proof receipts, and native
numerical values. Re-executing OpenSTA additionally requires the original local
waveforms and mapped design recorded in the evidence.
