# Artifact retention

`results/` is research evidence. `out/` holds scratch outputs and reusable
builds. Container removal does not remove these host files.

Preserve ledgers, workloads, calibration, summaries, activity measurements,
provenance, netlists and Liberty files. Keep active held-out outputs and build
caches. Once a run is retired, its VCD/FST/SAIF traces can be regenerated from
retained workloads and source provenance; they are not kept indefinitely.

```bash
.venv/bin/python maintenance/clean_artifacts.py \
  --plan out/.maintenance/example.json --targets explicit-old-run
# Inspect the plan before deletion:
.venv/bin/python maintenance/clean_artifacts.py \
  --plan out/.maintenance/example.json --apply --retire
```

Planning is read-only and records exact file identities, sizes and timestamps.
Applying rechecks identities, rejects active run references, tracked files,
symlinks, path escapes and protected build/evaluation directories. Deletion
is limited to the enumerated waveform files and has an audit log. `--retire`
moves the remaining directory to `out/retired/`, without deleting evidence.
`--skip-unwritable` emits a separate `.remaining.json` plan and leaves its
directories in place. Never use broad recursive deletion on `out/` or a
shared Docker prune to solve artifact accumulation.

## 2026-09-05 cleanup

Across 36 explicit old runs, 106,853 waveform files (640,764,080,128 allocated
bytes, about 641 GB) were removed and 34 cleaned directories moved under
`out/retired/`. Non-waveform evidence was preserved. These raw traces are not
recoverable from trash; regeneration requires the retained workload and flow.
Active held-out directories and their executable source digests were unchanged.

16,000 remaining root-owned traces occupy 505,584,082,944 allocated bytes
(about 506 GB) in `ibex-full` and `aes-baseline-matrix-docker-seed1`.
Passwordless sudo is unavailable. To finish only the validated remainder:

```bash
sudo /usr/bin/python3 maintenance/clean_artifacts.py \
  --plan out/.maintenance/stale-waveforms-20260905.remaining.json --apply --retire
```

Detailed plans and deletion logs remain in `out/.maintenance/`. A changed
file or active reference causes refusal rather than deleting new work.
Shared Docker inventory was inspected but not globally pruned; future builds
and containers use the project-scoped wrappers in `docker/`.
