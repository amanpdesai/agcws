# Independent accounting audit evidence

Findings and claim limits are in [RESULTS.md](../../RESULTS.md). The checklist was
committed at `cb4b6f351` before computing audit outcomes. This is a post-hoc audit
of the frozen study, not a new experimental protocol or provider billing audit.

| Artifact | Purpose |
|---|---|
| `reconstruction.json.gz` | All-cell measured-count loss/AUC reconstruction, paired inference, qualification, request/cost and cache accounting |
| `access.json.gz` | Final raw-local corroboration, independent schema checks, progress and input-visibility diagnostics |
| `access_initial.json.gz` | Preserved first pass, including an incorrect audit expectation about smoke progress |
| `information_access.json` | Source-reviewed actor/input table and interpretation limits |
| `verification.json` | Test/reproduction status and initial-check correction |
| `inventory.json` | Audit code, evidence and frozen input hashes |

Independent arithmetic imports no original/current experiment loss, summary,
history, policy-generation or cost helpers. The trapezoid is computed with
endpoint weights; paired inference uses six seed units. Static source review
was used to identify execution conventions. Integer bin counts are trusted
archived measurements: no waveforms were resimulated or independently recounted
in this slice. Numerical comparisons use absolute/relative tolerance 1e-10.
Here "independent" means a separate implementation, not a blinded independent
investigator, a second laboratory or newly collected measurements.

## Reproduce

Create a new [verified review view](../PACKED_EVIDENCE.md), then run from the
current repository root:

```bash
PYTHONPATH=src .venv/bin/python -m agcws.pipeline evidence-extract \
  --study nonflat_temporal_v1 --destination /tmp/accounting-review
PYTHONPATH=src .venv/bin/python -m analysis.accounting_audit \
  --archive /tmp/accounting-review/results/nonflat_temporal_v1 \
  --out /tmp/reconstruction.json.gz
.venv/bin/pytest -q tests/test_accounting_audit.py
PYTHONPATH=src .venv/bin/python -m analysis.accounting_inventory --verify
```

Outputs must not already exist. Compressed results are ordinary gzip JSON.
Audit commands write all detected discrepancies and return nonzero if any remain.
The optional local corroboration also needs the original run directory:

```bash
PYTHONPATH=src .venv/bin/python -m analysis.accounting_access \
  --archive /tmp/accounting-review/results/nonflat_temporal_v1 \
  --scratch out/nonflat-temporal-v1 --out /tmp/access.json.gz
```

That command checks local service/progress/request files against the published
archive. A clean clone has the primary accounting evidence but not these local
logs. Missing local records are a limitation, not permission to fabricate them.
Published per-file checksums preserve exactly what this local comparison covered.

The integration test restores a disposable view and deliberately corrupts one
trial loss to verify detection. It does not modify published evidence, call an
API or simulate hardware. No original result or scoring convention was changed.
