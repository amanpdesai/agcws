# Task-quality audit evidence — in progress

No model calls, new simulations or full comparative panel. Existing v6 banks
remain untouched. Scientific launch gate is not yet closed; see
[audit findings](../../docs/TASK_QUALITY_AUDIT.md).

- `scorecards.json`: ninety targets, independent witness/constant-floor
  calculations, pairwise geometry, witness cross-solves, and 180 independently
  recomputed classical engineering-smoke cells.
- `inputs.json.gz`: compact source JSON for these calculations, with original
  file hashes and canonical decoded-content hashes. This includes programs and
  witnesses and is **audit-only**, never model context or initialization data.
- `waveforms.json`: separate raw-waveform recount of confirmation burst and
  flat-control witnesses for the four identifier-event backends; eight traces,
  fixed selection, no selection by outcome. These are unweighted bit counts,
  not power. Ibex's distinct marker/bit-count contract is not covered by this
  particular recount.

Reproduce the scorecards with no scratch directories or external tools:

```bash
.venv/bin/python analysis/task_quality_audit.py \
  --inputs results/task_quality_v1/inputs.json.gz \
  --output /tmp/agcws-task-scorecards-check.json
cmp results/task_quality_v1/scorecards.json /tmp/agcws-task-scorecards-check.json
```

Output paths must not already exist. Recount raw waveforms, when the named
scratch traces are available, with `analysis/task_waveform_audit.py --output
<new-path>`. Waveform hashes and exact inputs are recorded; the compact JSON
archive is not a replacement for waveforms and cannot independently resimulate
the designs. Engineering data are exposed, not unseen-task evidence.
