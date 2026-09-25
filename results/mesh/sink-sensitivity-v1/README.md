# Mesh sink-setting sensitivity

Post-search replay fixes sink period to 8 and clamps pause to 0–3. It preserves
the selected workloads' other fields, targets, validity checks and 0.05 gate.
Selection uses the original power-finalist rule. There is no new search or AUC.

All 16 changed finalists complete RTL and mapped-power replay. The other 164
already satisfy these settings and retain their original measurements. Nonflat
matches remain 80/80 for Gemini and 20/80 for Flash-Lite. Flash-Lite controls
change from 7/10 to 6/10. Detailed counts and power errors are in `summary.json`.

`evidence.json.gz` contains checksummed native measurements, completion receipts,
power reports, frozen selection metadata and the exact executed script. Initial
source-path-check failures are retained. Waveforms remain external and are not
needed to verify the archived arithmetic.

Verify and regenerate the summary from the repository root:

```bash
PYTHONPATH=src .venv/bin/python -m agcws.reporting.mesh_sensitivity
```

The maintained replay runner is `agcws.evaluation.power.mesh_sensitivity`.
Its `--out` and `--workers` options select a new local collection and concurrency.
Replay requires the frozen runtimes and synthesis collateral identified in the
evidence. It makes no model calls and never overwrites the original search data.
