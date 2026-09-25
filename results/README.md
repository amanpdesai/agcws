# Final paper results

[Findings and tables](../docs/RESULTS.md) summarize the completed study.
[index.json](index.json) locates the files used by extraction and verification.

```text
results/
  summaries/       Aggregate search, statistics and power results
  aes/             Same layout for dma, ibex, mesh and redmule
    tasks/         Frozen targets, calibration evidence and study plans
    baselines/     Phase-random, phase-GA and phase-model archives
    flash_lite/    Gemini 3.5 Flash-Lite archives
    gemini_3_8/    Gemini 3.8 Flash archives and retained-cache records
    power/         Compressed measurements, references and failures
```

Archives retain their original contents, including failed proposals and recorded
paths. The index resolves those paths to current locations. Power records retain
original failures alongside the evidence used to recover their measurements.

[Power revision v2](power-revision-v2.json) identifies the 40 activity-qualified
references and the completed Ibex and RedMulE clipping audits. Each design's
`tasks/repaired-references-v1/` holds reference construction and qualification
evidence. `power/repaired-references-v1/` holds its power measurements.
`ibex/power/slew-validation-v1/` adds validation to unchanged candidate estimates.
`redmule/power/slew-recovery-v1/` recovers 22 measurements with verified clipping
and unchanged native power. Verify them with
`python -m agcws.reporting.redmule_recovery`.
The original compressed measurements remain intact.

[Mesh sensitivity](mesh/sink-sensitivity-v1/README.md) records the separate
fixed-sink replay and its reproducible measurements. Original search tables and
power comparisons are not overwritten by that sensitivity result.

Verify a search archive without restoring it:

```bash
python -m agcws evidence verify --study results/aes/baselines
```

Regenerate strong and power summaries, then the paper:

```bash
.venv/bin/python paper/scripts/extract_strong.py
.venv/bin/python paper/scripts/extract_power.py
.venv/bin/python paper/scripts/build.py --tectonic out/tools/tectonic-0.15.0/tectonic --submission
```

To reproduce the original reference comparison separately, use
`extract_power.py --original-references --out /tmp/original-power.json`.

Baseline and Flash summaries remain byte-identical published aggregates. Their
full trial archives are retained for independent verification. The paper build
checks pairing and aggregate arithmetic rather than rerunning experiments.

This directory contains only the final study and its supporting evidence.
