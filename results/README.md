# Final paper results

[Findings and tables](../docs/RESULTS.md) summarize the study.
[index.json](index.json) locates the final data and verification inputs.

```text
results/
  summaries/                  Aggregate search and power results
  <design>/                   aes, dma, ibex, mesh, redmule
    tasks/                    Targets, calibration and study plans
      references/             Reference workloads and qualification evidence
    baselines/                Classical search archives
    flash_lite/               Gemini 3.5 Flash-Lite archives
    gemini_3_8/                Gemini 3.8 Flash archives
    power/
      measurements.jsonl.gz   Final candidate and reference measurements
      validation/             Power validation evidence and audit receipts
  mesh/sink-sensitivity/      Separate fixed-sink replay
```

Each power archive contains 450 candidate measurements and nine references,
including controls. These are the records used directly by the paper, with no
replacement or revision files to apply. Reference qualification and clipping
checks remain reproducible from the supporting evidence. Historical paths in
native receipts identify their sources, not additional local dependencies.

Mesh sink sensitivity is a separate experiment. It does not replace the search
results or the main power comparison.

Verify a search archive without restoring it:

```bash
python -m agcws evidence verify --study results/aes/baselines
```

Verify the final power evidence and regenerate its summary, then build the paper:

```bash
PYTHONPATH=src .venv/bin/python paper/scripts/extract_power.py
PYTHONPATH=src .venv/bin/python paper/scripts/build.py --tectonic out/tools/tectonic-0.15.0/tectonic --submission
```

These checks validate stored evidence and comparison arithmetic. They do not
rerun simulation or OpenSTA. Superseded measurements are available in Git history.
